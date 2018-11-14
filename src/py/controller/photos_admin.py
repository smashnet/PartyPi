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
from services.photo_service import PhotoService

class PhotosAdminController(BaseController):

  @cherrypy.expose
  def index(self):
    # Collect photo thumburls
    template_vars = {}
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
      "href": "/admin/subscriptions"
    }
    ]
    
    photos = PhotoService.getListOfAllPhotos()
    if photos is not None:
      template_vars["photos"] = photos
      # Prune dateUploaded
      for item in template_vars["photos"]:
        item["dateUploaded"] = item["dateUploaded"].split('.')[0]
    template_vars["bodyclass"] = "class=main"
    return self.render_template("photos_admin/index.html", template_vars)
