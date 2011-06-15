import os, sys
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

