#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,datetime
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from settings import *
from domains.models import *

try:
	recType = sys.argv[1]
except:
	recType = "pri"

for d in list(domain.objects.filter(dns=True)):
	if recType == "sec":
		sec = "zone \"%s\" IN {\n"%d.name
		sec += "	type slave;\n"
		sec += "	file \"sec_auto/%s.zone\";\n"%d.name
		sec += "	allow-query { any; };\n"
		sec += "	masters { 87.236.194.121; };\n"
		sec += "};\n"
		print sec
	else:
		pri = "zone \"%s\" IN {\n"%d.name
		pri += "	type master;\n"
		pri += "	file \"pri_auto/%s.zone\";\n"%d.name
		pri += "	allow-query { any; };\n"
		pri += "	allow-transfer { 89.111.104.70; };\n"
		pri += "	notify yes;\n"
		pri += "};\n"
		print pri


