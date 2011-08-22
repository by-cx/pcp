# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^add/?$', 'mysql.views.add'),
		(r'^show/?$', 'mysql.views.show'),
		(r'^show/([0-9]{1,11})/?$', 'mysql.views.show'),
		(r'^rm/([a-z0-9\_\-]*)/?$', 'mysql.views.rm'),
		(r'^passwd/([a-zA-Z0-9\_\-]*)/?','mysql.views.passwd'),
)
