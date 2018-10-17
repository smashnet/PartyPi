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

DB_STRING = os.path.abspath(os.getcwd()) + "/data/data.db"
PHOTO_DIR = os.path.abspath(os.getcwd()) + "/data/img"
VERSION = "0.0.1"

class PartyPi(object):
  @cherrypy.expose
  def index(self):
    return open('html/index.html')

@cherrypy.expose
class PhotoUploadService(object):

  def imageExists(self, md5):
    with sqlite3.connect(DB_STRING) as c:
      r = c.execute("SELECT * FROM files WHERE md5=? LIMIT 1", (md5,))
      if len(r.fetchall()) == 0:
        return False
      else:
        return True


  @cherrypy.tools.json_out()
  def POST(self, file):
    size = 0
    whole_data = bytearray() # Neues Bytearray
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
      written_file = open(PHOTO_DIR + "/%s" % res["filename"], "wb") # open file in write bytes mode
      written_file.write(whole_data) # write file
      print(res)
      
      # Rotate image based on exif orientation
      try:
        image=Image.open(PHOTO_DIR + "/%s" % res["filename"])
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
        image.save(PHOTO_DIR + "/%s" % file.filename)
        image.close()

      except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass



      with sqlite3.connect(DB_STRING) as c:
        c.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?)", 
          [res['id'], res['filename'], res['filename_orig'], res['content_type'], res['md5'], res['uploader'], res['dateUploaded']])
    
      return res
    else:
      res = {"error": "Image already existing!"}
      print(res)
      return res

@cherrypy.expose
class PhotoWebService(object):

  @cherrypy.tools.accept(media='application/json')
  @cherrypy.tools.json_out()
  def GET(self, photoid='*', limit=0):
    with sqlite3.connect(DB_STRING) as c:
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
      with sqlite3.connect(DB_STRING) as c:
        r = c.execute("SELECT filename FROM files WHERE fileID=?", (str(photoid),))
        filename = r.fetchone()
        if filename is None:
          return {"error": "The photo with the provided id does not exist"}
      try:
        os.remove(PHOTO_DIR + "/%s" % str(filename[0]))
      except FileNotFoundError:
        print("File %s already gone" % str(filename[0]))
      
      # Delete photos from DB
      with sqlite3.connect(DB_STRING) as c:
        c.execute("DELETE FROM files WHERE fileID=?", (str(photoid),))
      

      return {"deleted": photoid}

@cherrypy.expose
class SubscriptionService(object):

  def mailExists(self, mail):
    with sqlite3.connect(DB_STRING) as c:
      r = c.execute("SELECT * FROM subscribers WHERE email=? LIMIT 1", (mail,))
      if len(r.fetchall()) == 0:
        return False
      else:
        return True

  @cherrypy.tools.json_out()
  def GET(self):
    # Get all subscribers
    with sqlite3.connect(DB_STRING) as c:
      r = c.execute("SELECT * FROM subscribers")
      descs = [desc[0] for desc in r.description]
      intermediate = r.fetchall()
      res = [dict(zip(descs, item)) for item in intermediate]
      print(res)
      return res
  
  @cherrypy.tools.json_out()
  def POST(self, mailaddress):
    # Check mail validity
    if not re.match(r"[^@]+@[^@]+\.[^@]+", mailaddress):
      return {"error": "Not a valid mail address"}

    res = {"id": str(uuid.uuid4()), "mail": mailaddress, "ip": cherrypy.request.remote.ip, "dateSubscribed": str(datetime.utcnow())}

    # Check if mail already exists
    if not self.mailExists(res['mail']):
      with sqlite3.connect(DB_STRING) as c:
        c.execute("INSERT INTO subscribers VALUES (?, ?, ?, ?)", 
          [res['id'], res['mail'], res['ip'], res['dateSubscribed']])
    
      res['message'] = 'Success!'
      return res
    else:
      return {"message": "You already subscribed!"}

  @cherrypy.tools.json_out()
  def DELETE(self, userid):
    # Delete user from DB
    if len(userid) == 0:
      return {"error": "No user provided for deletion"}
    else:
      with sqlite3.connect(DB_STRING) as c:
        c.execute("DELETE FROM subscribers WHERE userID=?", (str(userid),))  

      return {"deleted": userid}


def setup():
  '''
  Create photos directory if not existing yet
  '''
  if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

  '''
  Create the 'general', 'files' and 'subscribers' tables in the database on server startup, if not existing yet
  '''
  with sqlite3.connect(DB_STRING) as con:
    con.execute("CREATE TABLE IF NOT EXISTS general (key, value)")
    con.execute("CREATE TABLE IF NOT EXISTS files (fileID, filename, filename_orig, content_type, md5, uploader, dateUploaded)")
    con.execute("CREATE TABLE IF NOT EXISTS subscribers (userID, email, ip, dateSubsribed)")

  '''
  Check DB version
  '''
  with sqlite3.connect(DB_STRING) as con:
    r = con.execute("SELECT value FROM general WHERE key='version' LIMIT 1")
    res = r.fetchall()
    if len(res) == 0:
      con.execute("INSERT INTO general VALUES (?, ?)", ["version", VERSION])
    elif VERSION == res[0][0]:
      # Program and DB run same version, everything OK!
      pass
    else:
      # Different versions! Please migrate!
      # TODO
      print("Running PartyPi v? with DB v?! Exiting...", (VERSION, res[0][0]))
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
          'tools.response_headers.headers': [('Content-Type', 'application/json')],
      },
      '/photoupload': {
          'request.dispatch': cherrypy.dispatch.MethodDispatcher()
          #'tools.response_headers.on': True,
          #'tools.response_headers.headers': [('Content-Type', 'application/json')],
      },
      '/subscription': {
          'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
          'tools.response_headers.on': True,
          'tools.response_headers.headers': [('Content-Type', 'application/json')],
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
  webapp.photoupload = PhotoUploadService()
  webapp.subscription = SubscriptionService()
  cherrypy.quickstart(webapp, '/', conf)
