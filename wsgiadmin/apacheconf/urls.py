# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^sites/?$', 'wsgiadmin.apacheconf.views.apache'),
		(r'^sites/([0-9]{1,10})/?$', 'wsgiadmin.apacheconf.views.apache'),
		(r'^addStatic/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.addStatic'),
		(r'^updateStatic/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.updateStatic'),
		(r'^updateWsgi/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.updateWsgi'),
		(r'^removeSite/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.removeSite'),
		(r'^reload/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.reload'),
        (r'^restart/([0-9]*)/?$', 'wsgiadmin.apacheconf.views.restart'),
		(r'^addWsgi/?$', 'wsgiadmin.apacheconf.views.addWsgi'),
)

