#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
sys.path.append('/home/cx/co/pcp')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wsgiadmin.settings'

from django.contrib.auth.models import User
from wsgiadmin.clients.models import Machine
from wsgiadmin.requests.request import SSHHandler

print "=" * 80
print "this command is deprecated, use ./manage.py commit instead"
print "=" * 80

m = Machine.objects.filter(name="illusio")[0]
u = User.objects.filter(username="cx")[0]


sh = SSHHandler(u, m)
sh.commit()
