#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, datetime
from wsgiadmin.apacheconf.models import UserSite

sys.path.append('/home/cx/co/pcp')
sys.path.append('/home/cx/co/pcp/wsgiadmin')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wsgiadmin.settings'

from django.conf import settings

from apacheconf.models import *

into = datetime.date(2010, 9, 24)
ttotal = 0

for s in UserSite.objects.all():
    days = 0
    t = s.pub_date
    total = 0
    while t <= into:
        total += s.pay
        t += datetime.timedelta(1)
        days += 1

    if total: print "%.2f" % total, "\t", s.owner.username, "\t", s.server_name
    ttotal += total

print ttotal
print days
