#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,datetime
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from settings import *
from domains.models import *

try:
	recType = sys.argv[1]
except:
	recType = "pri"

open(ROOT+"signals/bind","w").close()
for d in list(domain.objects.filter(dns=True)):
	open(ROOT+"signals/zones/"+d.name,"w").close()
