# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^show/?$', 'wsgiadmin.users.views.show'),
		(r'^show/([0-9]{1,11})/?$', 'wsgiadmin.users.views.show'),
		(r'^rm/([0-9]{1,11})/?$', 'wsgiadmin.users.views.rm'),
		(r'^add/?$', 'wsgiadmin.users.views.add'),
		(r'^ssh_passwd/?$', 'wsgiadmin.users.views.ssh_passwd'),
		(r'^install/([0-9]{1,11})/?','wsgiadmin.users.views.install'),
		(r'^update/([0-9]{1,11})/?$', 'wsgiadmin.users.views.update'),
		(r'^update/switch/user/([0-9]{1,11})/([0-9]{1,11})/?$', 'wsgiadmin.users.views.switch_to_user'),
		(r'^update/switch/admin/([0-9]{1,11})/?$', 'wsgiadmin.users.views.switch_to_admin'),
)
