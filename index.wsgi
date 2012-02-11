import os, sys
from os.path import dirname, basename, join, pardir

activate_this = '/home/pcp/virtualenvs/pcp/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

django_settings_module = 'wsgiadmin.settings'
pythonpath = [
    dirname(__file__),
]

sys.path = pythonpath + sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
