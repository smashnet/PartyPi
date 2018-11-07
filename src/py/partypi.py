'''
partypi.py

Main file of PartyPi.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import os, os.path
import sys
from datetime import datetime
import random
import string
import uuid
import re

import cherrypy
import sqlite3
try: import simplejson as json
except ImportError: import json
import hashlib
from PIL import Image, ExifTags

import config

class PartyPi(object):
  @cherrypy.expose
  def index(self):
    return open('src/html/index.html')

@cherrypy.expose
class PhotoUploadService(object):

  def imageExists(self, md5):
    with sqlite3.connect(config.DB_STRING) as c:
      r = c.execute("SELECT * FROM files WHERE md5=? LIMIT 1", (md5,))
      if len(r.fetchall()) == 0:
        return False
      else:
        return True

  def rotateIfNecessary(self, img):
    # Rotate image based on exif orientation
    try:
      image=Image.open(config.PHOTO_DIR + "/%s" % img)
      for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation]=='Orientation':
          break
      exif=dict(image._getexif().items())

      if exif[orientation] == 3:
        image=image.rotate(180, expand=True)
      elif exif[orientation] == 6:
        image=image.rotate(270, expand=True)
      elif exif[orientation] == 8:
        image=image.rotate(90, expand=True)
      image.save(config.PHOTO_DIR + "/%s" % img)
      image.close()

    except (AttributeError, KeyError, IndexError):
      # cases: image don't have getexif
      pass

  def createThumbs(self, img):
    small = 128, 128
    medium = 512, 512
    large = 1024, 1024
    fn, filext = os.path.splitext(img)
    image = Image.open(config.PHOTO_DIR + "/%s" % img)

    thumb_small = image.copy()
    thumb_small.thumbnail(small)
    thumb_small.save(config.PHOTO_THUMBS_DIR + "/%s_128px%s" %(fn, filext))

    thumb_mid = image.copy()
    thumb_mid.thumbnail(medium)
    thumb_mid.save(config.PHOTO_THUMBS_DIR + "/%s_512px%s" %(fn, filext))

    thumb_large = image.copy()
    thumb_large.thumbnail(large)
    thumb_large.save(config.PHOTO_THUMBS_DIR + "/%s_1024px%s" %(fn, filext))

  @cherrypy.tools.json_out()
  def POST(self, file):
    size = 0
    whole_data = bytearray()
    filehash = hashlib.md5()

    while True:
      data = file.file.read(8192)
      filehash.update(data)
      whole_data += data # Save data chunks in ByteArray whole_data

      if not data:
        break
      size += len(data)

    img_uuid = str(uuid.uuid4())
    fn, filext = os.path.splitext(file.filename)
    res = {"id": img_uuid, "filename_orig": file.filename, "filename": '%s%s' % (img_uuid, filext), "content_type": str(file.content_type), "md5": filehash.hexdigest(), "uploader": cherrypy.request.remote.ip, "dateUploaded": str(datetime.utcnow())}


    if not self.imageExists(res['md5']):
      written_file = open(config.PHOTO_DIR + "/%s" % res["filename"], "wb") # open file in write bytes mode
      written_file.write(whole_data) # write file

      # Rotate image if necessary
      self.rotateIfNecessary(res['filename'])

      # Create thumbnails
      self.createThumbs(res['filename'])

      with sqlite3.connect(config.DB_STRING) as c:
        c.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?)",
          [res['id'], res['filename'], res['filename_orig'], res['content_type'], res['md5'], res['uploader'], res['dateUploaded']])

      return res
    else:
      res = {"error": "Image already existing!"}
      print(res)
      return res

@cherrypy.expose
class ThumbnailService(object):

  @cherrypy.tools.accept(media='application/json')
  def GET(self, photouuid=None, size='512px'):
    # Check if is valid uuid
    try:
      res = uuid.UUID(photouuid, version=4)
    except ValueError:
      return "Not a valid uuid"

    # Check if is valid size
    if size == "128px" or size == "512px" or size == "1024px":
      # Get file information from DB
      with sqlite3.connect(config.DB_STRING) as c:
        r = c.execute("SELECT * FROM files WHERE fileID=?", (str(photouuid),))
        res = r.fetchone()
        fn, filext = os.path.splitext(res[1])
        with open(config.PHOTO_THUMBS_DIR + "/%s_%s%s" % (photouuid, size, filext), "rb") as the_file:
          cherrypy.response.headers['Content-Type'] = 'image/jpeg'
          return the_file.read()

@cherrypy.expose
class PhotoWebService(object):

  @cherrypy.tools.accept(media='application/json')
  @cherrypy.tools.json_out()
  def GET(self, photoid='*', limit=0):
    with sqlite3.connect(config.DB_STRING) as c:
      if photoid == '*':
        if limit == 0:
          r = c.execute("SELECT * FROM files")
        else:
          r = c.execute("SELECT * FROM files LIMIT ?", (int(limit),))

      else:
        if limit == 0:
          r = c.execute("SELECT * FROM files WHERE fileID=?", (str(photoid),))
        else:
          r = c.execute("SELECT * FROM files WHERE fileID=? LIMIT ?", (str(photoid),int(limit)))

      descs = [desc[0] for desc in r.description]
      intermediate = r.fetchall()
      res = [dict(zip(descs, item)) for item in intermediate]
      print(res)
      return res

  @cherrypy.tools.accept(media='application/json')
  @cherrypy.tools.json_out()
  def DELETE(self, photoid):
    if len(photoid) == 0:
      return {"error": "No photos provided for deletion"}
    else:
      # Delete photos from storage
      with sqlite3.connect(config.DB_STRING) as c:
        r = c.execute("SELECT filename FROM files WHERE fileID=?", (str(photoid),))
        filename = r.fetchone()
        if filename is None:
          return {"error": "The photo with the provided id does not exist"}
      try:
        os.remove(config.PHOTO_DIR + "/%s" % str(filename[0]))
      except FileNotFoundError:
        print("File %s already gone" % str(filename[0]))

      # Delete photos from DB
      with sqlite3.connect(config.DB_STRING) as c:
        c.execute("DELETE FROM files WHERE fileID=?", (str(photoid),))


      return {"deleted": photoid}

@cherrypy.expose
class SubscriptionService(object):

  def mailExists(self, mail):
    with sqlite3.connect(config.DB_STRING) as c:
      r = c.execute("SELECT * FROM subscribers WHERE mail=? LIMIT 1", (mail,))
      if len(r.fetchall()) == 0:
        return False
      else:
        return True

  def getAllSubscribers(self):
    with sqlite3.connect(config.DB_STRING) as c:
      r = c.execute("SELECT uuid, mail, ip, dateSubscribed FROM subscribers")
      descs = [desc[0] for desc in r.description]
      intermediate = r.fetchall()
      res = [dict(zip(descs, item)) for item in intermediate]
      return res

  def getSingleSubscriber(self, uuid):
    with sqlite3.connect(config.DB_STRING) as c:
      r = c.execute("SELECT uuid, mail, ip, dateSubscribed FROM subscribers WHERE uuid=?", (str(uuid),))
      descs = [desc[0] for desc in r.description]
      intermediate = r.fetchall()
      res = [dict(zip(descs, item)) for item in intermediate]
      return res

  @cherrypy.tools.json_out()
  def GET(self, subscriberuuid=None):

    if subscriberuuid is None:
      return {"error": "No UUID"}

    # If parameter is "all" return all subscriptions
    if subscriberuuid == "all":
      return self.getAllSubscribers()

    # Check if is valid uuid
    try:
      res = uuid.UUID(subscriberuuid, version=4)
    except ValueError:
      return {"error": "Not a UUID"}

    # Return single subscriber information
    return self.getSingleSubscriber(subscriberuuid)

  @cherrypy.tools.json_out()
  def POST(self, mailaddress):
    # Check mail validity
    if not re.match(r"[^@]+@[^@]+\.[^@]+", mailaddress):
      return {"error": "Not a valid mail address"}

    res = {"id": str(uuid.uuid4()), "mail": mailaddress, "ip": cherrypy.request.remote.ip, "dateSubscribed": str(datetime.utcnow())}

    # Check if mail already exists
    if not self.mailExists(res['mail']):
      with sqlite3.connect(config.DB_STRING) as c:
        c.execute("INSERT INTO subscribers VALUES (?, ?, ?, ?)",
          [res['id'], res['mail'], res['ip'], res['dateSubscribed']])

      return res
    else:
      return {"error": "You already subscribed!"}

  @cherrypy.tools.json_out()
  def DELETE(self, userid):
    # Delete user from DB
    if len(userid) == 0:
      return {"error": "No user provided for deletion"}
    else:
      with sqlite3.connect(config.DB_STRING) as c:
        c.execute("DELETE FROM subscribers WHERE userID=?", (str(userid),))

      return {"deleted": userid}


def setup():
  '''
  Create directories if not existing yet
  '''
  if not os.path.exists(config.PHOTO_DIR):
    os.makedirs(config.PHOTO_DIR)

  if not os.path.exists(config.PHOTO_THUMBS_DIR):
    os.makedirs(config.PHOTO_THUMBS_DIR)

  '''
  Create the 'general', 'files' and 'subscribers' tables in the database on server startup, if not existing yet
  '''
  with sqlite3.connect(config.DB_STRING) as con:
    con.execute("CREATE TABLE IF NOT EXISTS general (key, value)")
    con.execute("CREATE TABLE IF NOT EXISTS files (fileID, filename, filename_orig, content_type, md5, uploader, dateUploaded)")
    con.execute("CREATE TABLE IF NOT EXISTS subscribers (uuid, mail, ip, dateSubscribed)")

  '''
  Check DB version
  '''
  with sqlite3.connect(config.DB_STRING) as con:
    r = con.execute("SELECT value FROM general WHERE key='version' LIMIT 1")
    res = r.fetchall()
    if len(res) == 0:
      con.execute("INSERT INTO general VALUES (?, ?)", ["version", config.VERSION])
    elif config.VERSION == res[0][0]:
      # Program and DB run same version, everything OK!
      pass
    else:
      # Different versions! Please migrate!
      # TODO
      print("Running PartyPi v? with DB v?! Exiting...", (config.VERSION, res[0][0]))
      sys.exit(100)


if __name__ == '__main__':
  conf = {
      '/': {
          'tools.sessions.on': False,
          'tools.staticdir.root': os.path.abspath(os.getcwd())
      },
      '/photos': {
          'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
          'tools.response_headers.on': True,
          'tools.response_headers.headers': [('Content-Type', 'application/json')]
      },
      '/thumbnail': {
          'request.dispatch': cherrypy.dispatch.MethodDispatcher()
      },
      '/photoupload': {
          'request.dispatch': cherrypy.dispatch.MethodDispatcher()
      },
      '/subscription': {
          'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
          'tools.response_headers.on': True,
          'tools.response_headers.headers': [('Content-Type', 'application/json')]
      },
      '/static': {
          'tools.staticdir.on': True,
          'tools.staticdir.dir': './static'
      }
  }
  cherrypy.server.socket_host = '0.0.0.0'
  cherrypy.server.socket_port = 8080

  cherrypy.engine.subscribe('start', setup)

  webapp = PartyPi()
  webapp.photos = PhotoWebService()
  webapp.thumbnail = ThumbnailService()
  webapp.photoupload = PhotoUploadService()
  webapp.subscription = SubscriptionService()
  cherrypy.quickstart(webapp, '/', conf)
