# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^add/?$', 'ftps.views.add'),
		(r'^show/?$', 'ftps.views.show'),
		(r'^show/([0-9]{1,11})/?$', 'ftps.views.show'),
		(r'^rm/([0-9]{1,11})/?$', 'ftps.views.rm'),
		(r'^update/([0-9]{1,11})/?$', 'ftps.views.update'),
		(r'^passwd/([0-9]{1,11})/?$', 'ftps.views.passwd'),
)
