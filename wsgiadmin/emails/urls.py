# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^email_info/?$', 'wsgiadmin.emails.views.emailInfo'),
		(r'^boxes/?$', 'wsgiadmin.emails.views.boxes'),
		(r'^boxes/([0-9]{1,10})/?$', 'wsgiadmin.emails.views.boxes'),
		(r'^add_box/?$', 'wsgiadmin.emails.views.addBox'),
		(r'^remove_box/([0-9]*)/?$', 'wsgiadmin.emails.views.removeBox'),
		(r'^change_passwd_box/([0-9]*)/?$', 'wsgiadmin.emails.views.changePasswdBox'),
		(r'^redirects/?$', 'wsgiadmin.emails.views.redirects'),
		(r'^redirects/([0-9]{1,10})/?$', 'wsgiadmin.emails.views.redirects'),
		(r'^add_redirect/?$', 'wsgiadmin.emails.views.addRedirect'),
		(r'^change_redirect/([0-9]*)/?$', 'wsgiadmin.emails.views.changeRedirect'),
		(r'^removeRedirect/([0-9]*)/?$', 'wsgiadmin.emails.views.removeRedirect'),

)

