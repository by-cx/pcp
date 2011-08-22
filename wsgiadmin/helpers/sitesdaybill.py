#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,datetime
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from django.conf import settings

from apacheconf.models import *

ttotal = 0

for s in site.objects.all():
	print "%f kč - %s"%(s.pay(), s.serverName)

		ttotal += s.pay()

print ttotal
