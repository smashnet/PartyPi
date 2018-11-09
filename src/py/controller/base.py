'''
partypi.py

Main file of PartyPi.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

from jinja2 import Environment, FileSystemLoader, select_autoescape

import config

class BaseController(object):

  def render_template(self, path, template_vars=None):
    fl = FileSystemLoader(config.VIEWS_PATH)
    env = Environment(loader=fl, autoescape=select_autoescape(["html"]))
    template_vars = template_vars if template_vars else {}
    template = env.get_template(path)
    return template.render(template_vars)
