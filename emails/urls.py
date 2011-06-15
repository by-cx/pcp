# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^email_info/?$', 'emails.views.emailInfo'),
		(r'^boxes/?$', 'emails.views.boxes'),
		(r'^boxes/([0-9]{1,10})/?$', 'emails.views.boxes'),
		(r'^add_box/?$', 'emails.views.addBox'),
		(r'^remove_box/([0-9]*)/?$', 'emails.views.removeBox'),
		(r'^change_passwd_box/([0-9]*)/?$', 'emails.views.changePasswdBox'),
		(r'^redirects/?$', 'emails.views.redirects'),
		(r'^redirects/([0-9]{1,10})/?$', 'emails.views.redirects'),
		(r'^add_redirect/?$', 'emails.views.addRedirect'),
		(r'^change_redirect/([0-9]*)/?$', 'emails.views.changeRedirect'),
		(r'^removeRedirect/([0-9]*)/?$', 'emails.views.removeRedirect'),

)

