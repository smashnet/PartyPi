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

class PhotosOverviewController(BaseController):

  @cherrypy.expose
  def index(self):
    # Collect photo thumburls
    template_vars = {}
    template_vars["photos"] = PhotoService.getListOfAllPhotos()
    template_vars["bodyclass"] = "class=main"
    print(template_vars)
    return self.render_template("photos_overview/index.html", template_vars)
