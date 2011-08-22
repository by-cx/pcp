#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,datetime
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from django.contrib.auth.models import User as user

from django.conf import settings

from apacheconf.models import *
from bills.tools import *

total = 0

for u in user.objects.all():
	data = aggregate(u)
	for item in data:
		print "%d kč - %s"%(data[item][0],item)
		total += data[item][0]

print
print "Celkem",total,"kč"
