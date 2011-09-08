#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
sys.path.append('/home/cx/co/pcp')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wsgiadmin.settings'

from wsgiadmin.requests.request import SSHHandler
from wsgiadmin.clients.models import Machine
from django.contrib.auth.models import User

m = Machine.objects.all()[0]
u = User.objects.all()[0]

sh = SSHHandler(u, m)
sh.commit()
