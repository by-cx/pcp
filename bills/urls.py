# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^bill/([a-z]*)/([0-9]*)/$', 'bills.views.show'),
)

