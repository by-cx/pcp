#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,logging
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from django.conf import settings

from rtools import *
from keystore.tools import *
from django.contrib.auth.models import User as user
from clients.models import *

for iu in user.objects.all():
	iu.parms
	try:
		iu.parms
	except:
		logging.info("Chybí parms uživatele %s"%iu.username)
		continue
	
	homedir = iu.parms.home
	if not homedir:
		logging.info("Chybí home uživatele %s"%iu.username)
		continue

	rr = request_raw(iu.parms.web_machine.ip)
	data = rr.run("du -s %s" % homedir)["stdout"]
		
	if data:
		raw = data.strip()
		if not raw:
			logging.info("Chybí home uživatele %s"%iu.username)
			continue
		
		kset("%s:homesize"%iu.username,str(int(raw.split("\t")[0])*1024),4320)
	else:
		pass
		logging.info("Chybí home uživatele %s"%iu.username)
		
