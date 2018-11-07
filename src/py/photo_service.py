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
from datetime import datetime
import uuid

import cherrypy
import sqlite3
import hashlib
from PIL import Image, ExifTags

import config

@cherrypy.expose
class PhotoService(object):

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

  def getListOfAllPhotos(self):
    with sqlite3.connect(config.DB_STRING) as c:
      r = c.execute("SELECT uuid, filename_orig, content_type, md5, uploader, dateUploaded FROM files")
      descs = [desc[0] for desc in r.description]
      intermediate = r.fetchall()
      res = [dict(zip(descs, item)) for item in intermediate]
      return res

  def getSinglePhoto(self, photouuid):
    with sqlite3.connect(config.DB_STRING) as c:
      r = c.execute("SELECT uuid, filename_orig, content_type, md5, uploader, dateUploaded FROM files WHERE uuid=?", (photouuid,))
      descs = [desc[0] for desc in r.description]
      intermediate = r.fetchall()
      res = [dict(zip(descs, item)) for item in intermediate]
      return res

  @cherrypy.tools.accept(media='application/json')
  @cherrypy.tools.json_out()
  def GET(self, photouuid=None, limit=0):
    # If no parameter is provided -> error
    if photouuid is None:
      return {"error": "No UUID"}

    # If parameter is "all" return all subscriptions
    if photouuid == "all":
      return self.getListOfAllPhotos()

    # Check if is valid uuid
    try:
      uuid.UUID(photouuid, version=4)
    except ValueError:
      return {"error": "Not a UUID"}

    # Return single subscriber information
    return self.getSinglePhoto(photouuid)

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

  @cherrypy.tools.accept(media='application/json')
  @cherrypy.tools.json_out()
  def DELETE(self, photoid):
    if len(photoid) == 0:
      return {"error": "No photos provided for deletion"}
    else:
      # Delete photos from storage
      with sqlite3.connect(config.DB_STRING) as c:
        r = c.execute("SELECT filename FROM files WHERE uuid=?", (str(photoid),))
        filename = r.fetchone()
        if filename is None:
          return {"error": "The photo with the provided id does not exist"}
      try:
        os.remove(config.PHOTO_DIR + "/%s" % str(filename[0]))
      except FileNotFoundError:
        print("File %s already gone" % str(filename[0]))

      # Delete photos from DB
      with sqlite3.connect(config.DB_STRING) as c:
        c.execute("DELETE FROM files WHERE uuid=?", (str(photoid),))


      return {"deleted": photoid}
