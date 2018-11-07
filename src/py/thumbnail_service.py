'''
thumbnail_service.py

Thumbnail service responsible for creating thumbnails of newly uploaded photos.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import os, os.path
import uuid

import cherrypy
import sqlite3

import config

@cherrypy.expose
class ThumbnailService(object):

  @cherrypy.tools.accept(media='application/json')
  def GET(self, photouuid=None, size='512px'):
    # Check if is valid uuid
    try:
      uuid.UUID(photouuid, version=4)
    except ValueError:
      return "Not a valid uuid"

    # Check if is valid size
    if size == "128px" or size == "512px" or size == "1024px":
      # Get file information from DB
      with sqlite3.connect(config.DB_STRING) as c:
        r = c.execute("SELECT * FROM files WHERE uuid=?", (str(photouuid),))
        res = r.fetchone()
        fn, filext = os.path.splitext(res[1])
        with open(config.PHOTO_THUMBS_DIR + "/%s_%s%s" % (photouuid, size, filext), "rb") as the_file:
          cherrypy.response.headers['Content-Type'] = 'image/jpeg'
          return the_file.read()
