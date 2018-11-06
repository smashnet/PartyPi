'''
config.py

Config file of PartyPi.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

import os, os.path

VERSION = "0.0.1"
DB_STRING = os.path.abspath(os.getcwd()) + "/data/data.db"
PHOTO_DIR = os.path.abspath(os.getcwd()) + "/data/img"
PHOTO_THUMBS_DIR = os.path.abspath(os.getcwd()) + "/data/img/thumbs"
