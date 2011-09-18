import os, sys
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/pcp')
sys.path.append('/home/cx/co/pcp/wsgiadmin')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wsgiadmin.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

