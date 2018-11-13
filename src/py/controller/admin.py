'''
partypi.py

Main file of PartyPi.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import cherrypy

from controller.base import BaseController

class AdminController(BaseController):

  @cherrypy.expose
  def index(self):
    template_vars = {"bodyclass": "class=main"}
    template_vars["title"] = {
    "name": "PartyPi - Administration",
    "href": "/admin"
    }
    # Set navbar links
    template_vars["navlinks"] = [
    {
      "name": "Home",
      "href": "/"
    },
    {
      "name": "Fotos",
      "href": "/admin/photos"
    },
    {
      "name": "Subscriptions",
      "href": "/admin/aubscriptions"
    }
    ]
    # Set admin area links# Set navbar links
    template_vars["adminlinks"] = [
    {
      "name": "Fotos",
      "href": "/admin/photos"
    },
    {
      "name": "Subscriptions",
      "href": "/admin/aubscriptions"
    }
    ]
    return self.render_template("admin/index.html", template_vars)
