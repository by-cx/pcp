#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from wsgiadmin.apacheconf.models import UserSite

sys.path.append('/home/cx/co/pcp')
sys.path.append('/home/cx/co/pcp/wsgiadmin')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wsgiadmin.settings'


ttotal = 0
sites =  UserSite.objects.all()
for s in sites:
    payment = s.pay
    print u"%f kč - %s" % (payment, s.server_name)

    ttotal += payment

print ttotal
