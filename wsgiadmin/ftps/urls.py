# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^add/?$', 'wsgiadmin.ftps.views.add'),
		(r'^show/?$', 'wsgiadmin.ftps.views.show'),
		(r'^show/([0-9]{1,11})/?$', 'wsgiadmin.ftps.views.show'),
		(r'^rm/([0-9]{1,11})/?$', 'wsgiadmin.ftps.views.rm'),
		(r'^update/([0-9]{1,11})/?$', 'wsgiadmin.ftps.views.update'),
		(r'^passwd/([0-9]{1,11})/?$', 'wsgiadmin.ftps.views.passwd'),
)
