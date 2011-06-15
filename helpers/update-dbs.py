#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from settings import *
from pgs.models import *

for signal in os.listdir(ROOT+"/signals/pgs/"):
	f = open(ROOT+"/signals/pgs/"+signal)
	data = f.read()
	f.close()
	
	owner = signal.split("_")[0]
	action = data.split("|")[0]
	db = signal
	
	if action == "create":
		os.system("/bin/su postgres -c \"/usr/bin/createdb -O %s %s\""%(owner,db))
	elif action == "remove":
		os.system("/bin/su postgres -c \"/usr/bin/dropdb %s\""%db)
	
	os.unlink(ROOT+"/signals/pgs/"+signal)