#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append('/home/cx/co/pcp')
sys.path.append('/home/cx/co/pcp/wsgiadmin')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wsgiadmin.settings'

from wsgiadmin.requests.request import SSHHandler

sh = SSHHandler(None, None)
sh.commit()
