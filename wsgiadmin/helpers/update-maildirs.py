#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from settings import *
from emails.models import *

HOME="/var/mail"

for e in list(email.objects.all()):
	maildir = "%s/%s/%s"%(HOME,e.domain.name,e.login)
	print maildir
