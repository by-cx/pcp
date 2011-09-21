#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, logging
from wsgiadmin.keystore.tools import kset
from wsgiadmin.requests.tools import RawRequest
from wsgiadmin.clients.models import *

sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

print "deprecated, use ./manage.py update_homesizes instead\n" * 5

for iu in user.objects.all():
    iu.parms
    try:
        iu.parms
    except:
        logging.info(u"Chybí parms uživatele %s" % iu.username)
        continue

    homedir = iu.parms.home
    if not homedir:
        logging.info(u"Chybí home uživatele %s" % iu.username)
        continue

    rr = RawRequest(iu.parms.web_machine.ip)
    data = rr.run("du -s %s" % homedir)["stdout"]

    if data:
        raw = data.strip()
        if not raw:
            logging.info(u"Chybí home uživatele %s" % iu.username)
            continue

        kset("%s:homesize" % iu.username, str(int(raw.split("\t")[0]) * 1024), 4320)
    else:
        logging.info(u"Chybí home uživatele %s" % iu.username)
