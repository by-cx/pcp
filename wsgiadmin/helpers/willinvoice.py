# -*- coding: utf-8 -*-

import os,sys
from wsgiadmin.bills.tools import create_invoices

sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

create_invoices(False,0)
