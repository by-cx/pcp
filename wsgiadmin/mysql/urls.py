# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^add/?$', 'wsgiadmin.mysql.views.add'),
		(r'^show/?$', 'wsgiadmin.mysql.views.show'),
		(r'^show/([0-9]{1,11})/?$', 'wsgiadmin.mysql.views.show'),
		(r'^rm/([a-z0-9\_\-]*)/?$', 'wsgiadmin.mysql.views.rm'),
		(r'^passwd/([a-zA-Z0-9\_\-]*)/?','wsgiadmin.mysql.views.passwd'),
)
