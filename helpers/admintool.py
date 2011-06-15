#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse,os,sys

sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from domains.tools import *
from domains.models import domain
from django.conf import settings
from requests.tools import request as push_request
from apacheconf.tools import gen_vhosts
from django.contrib.auth.models import User as user

parser = argparse.ArgumentParser(description='Rosti admintool')
parser.add_argument('-z', "--zones", dest='zones', action='store_true', default=False, help='Generate all new zones file')
parser.add_argument('-c', "--config", dest='config', action='store_true', default=False, help='Reload Apache config')

args = parser.parse_args()

if args.zones:
	print "Generating all new zones"
	for d in domain.objects.all():
		print d.name
		push_request("bind_add_zone", settings.PRIMARY_DNS, {"domain": d.name, "zone": gen_zone_config(d)}).save()
elif args.config:
	print "Reloading Apache and uWSGI config"

	for m in list(set([u.parms.web_machine for u in user.objects.all()])):
		push_request("apache_reload", m.ip, {"vhosts": gen_vhosts()}).save()
	
else:
	parser.print_help()
