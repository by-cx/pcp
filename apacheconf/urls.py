# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^sites/?$', 'apacheconf.views.apache'),
		(r'^sites/([0-9]{1,10})/?$', 'apacheconf.views.apache'),
		(r'^addStatic/([0-9]*)/?$', 'apacheconf.views.addStatic'),
		(r'^updateStatic/([0-9]*)/?$', 'apacheconf.views.updateStatic'),
		(r'^updateWsgi/([0-9]*)/?$', 'apacheconf.views.updateWsgi'),
		(r'^removeSite/([0-9]*)/?$', 'apacheconf.views.removeSite'),
		(r'^reload/([0-9]*)/?$', 'apacheconf.views.reload'),
        (r'^restart/([0-9]*)/?$', 'apacheconf.views.restart'),
		(r'^addWsgi/?$', 'apacheconf.views.addWsgi'),
)

