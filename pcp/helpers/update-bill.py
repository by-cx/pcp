#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,logging
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from django.conf import settings

from bills.tools import *

if "service" in sys.argv:
	bill_services()
if "hosting" in sys.argv:
	bill_hosting()
if "invoices" in sys.argv:
	create_invoices()

