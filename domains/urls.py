# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^registration/?$', 'domains.views.registration'),
		(r'^check/?$', 'domains.views.check'),
		(r'^add/?$', 'domains.views.add'),
		(r'^show/?$', 'domains.views.show'),
		(r'^show/([0-9]{1,11})/?$', 'domains.views.show'),
		(r'^rm/([0-9]{1,11})/?$', 'domains.views.rm'),
)
