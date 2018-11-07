'''
common.py

Holds severals functions commonly used in PartyPi.

Author: Nicolas Inden
eMail: nico@smashnet.de
GPG-Key-ID: B2F8AA17
GPG-Fingerprint: A757 5741 FD1E 63E8 357D  48E2 3C68 AE70 B2F8 AA17
License: MIT License
'''

def DBtoDict(res):
  descs = [desc[0] for desc in res.description]
  intermediate = res.fetchall()
  return [dict(zip(descs, item)) for item in intermediate]
