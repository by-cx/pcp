# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^show/?$', 'users.views.show'),
		(r'^show/([0-9]{1,11})/?$', 'users.views.show'),
		(r'^rm/([0-9]{1,11})/?$', 'users.views.rm'),
		(r'^add/?$', 'users.views.add'),
		(r'^ssh_passwd/?$', 'users.views.ssh_passwd'),
		(r'^install/([0-9]{1,11})/?','users.views.install'),
		(r'^update/([0-9]{1,11})/?$', 'users.views.update'),
		(r'^update/switch/user/([0-9]{1,11})/([0-9]{1,11})/?$', 'users.views.switch_to_user'),
		(r'^update/switch/admin/([0-9]{1,11})/?$', 'users.views.switch_to_admin'),
)
