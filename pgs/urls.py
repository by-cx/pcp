# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^add/?$', 'pgs.views.add'),
		(r'^show/?$', 'pgs.views.show'),
		(r'^show/([0-9]{1,11})/?$', 'pgs.views.show'),
		(r'^rm/([a-z0-9\_\-]*)/?$', 'pgs.views.rm'),
		(r'^passwd/([a-zA-Z0-9\_\-]*)/?','pgs.views.passwd'),
)
