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

import cherrypy
import sqlite3

import config
from thumbnail_service import ThumbnailService
from photo_service import PhotoService
from subscription_service import SubscriptionService

class PartyPi(object):

  @cherrypy.expose
  def default(self, *args, **kwargs):
    return open('src/html/404.html')

  @cherrypy.expose
  def index(self):
    return open('src/html/index.html')

  @cherrypy.expose
  def admin(self):
    return open('src/html/photos_admin.html')


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
    con.execute("CREATE TABLE IF NOT EXISTS files (uuid, filename, filename_orig, content_type, md5, uploader, dateUploaded)")
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
      '/photo': {
          'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
          'tools.response_headers.on': True,
          'tools.response_headers.headers': [('Content-Type', 'application/json')]
      },
      '/thumbnail': {
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
  webapp.photo = PhotoService()
  webapp.thumbnail = ThumbnailService()
  webapp.subscription = SubscriptionService()
  cherrypy.quickstart(webapp, '/', conf)
