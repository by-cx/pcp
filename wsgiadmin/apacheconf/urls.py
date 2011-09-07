# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^sites/?$', 'wsgiadmin.apacheconf.views.apache'),
		(r'^sites/([0-9]{1,10})/?$', 'wsgiadmin.apacheconf.views.apache'),
		(r'^addStatic/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.add_static'),
		(r'^updateStatic/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.update_static'),
		(r'^updateWsgi/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.update_wsgi'),
		(r'^removeSite/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.remove_site'),
		(r'^reload/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.reload'),
        (r'^restart/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.restart'),
		(r'^addWsgi/?$', 'wsgiadmin.apacheconf.views.add_wsgi'),
)

