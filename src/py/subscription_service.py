'''
subscription_service.py

PartyPis subscription service is responsible for holding subscriber information.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

from datetime import datetime
import uuid
import re

import cherrypy
import sqlite3

import config

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
    # If no parameter is provided -> error
    if subscriberuuid is None:
      return {"error": "No UUID"}

    # If parameter is "all" return all subscriptions
    if subscriberuuid == "all":
      return self.getAllSubscribers()

    # Check if is valid uuid
    try:
      uuid.UUID(subscriberuuid, version=4)
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
