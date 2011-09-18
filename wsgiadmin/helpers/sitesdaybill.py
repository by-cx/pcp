#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from wsgiadmin.apacheconf.models import UserSite

sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'


ttotal = 0
sites =  UserSite.objects.all()
for s in sites:
    payment = s.pay
    print "%f kč - %s" % (payment, s.serverName)

    ttotal += payment

print ttotal
