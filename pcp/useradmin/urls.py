# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^/?$', 'useradmin.views.info'),
		(r'^domains/', include('domains.urls')),
        (r'^bills/', include('bills.urls')),
		(r'^ftp/', include('ftps.urls')),
        (r'^email/', include('emails.urls')),
        (r'^apache/', include('apacheconf.urls')),
		(r'^pg/', include('pgs.urls')),
		(r'^users/', include('users.urls')),
		(r'^mysql/', include('mysql.urls')),
        (r'^reg/?$', 'useradmin.views.reg'),
        (r'^reg-ok/?$', 'useradmin.views.regok'),
		(r"^message/([a-z]{1,20})/(.{1,100})?$","useradmin.views.message"),
		(r'^login/?$', 'django.contrib.auth.views.login', {'template_name': 'login_reg.html'}),
		(r'^logout/?$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}),
		(r'^change_passwd/?$', 'useradmin.views.changePasswd'),
		(r'^ok/?$', 'useradmin.views.ok'),
		(r'^error/?$', 'useradmin.views.error'),
		(r'^info/?$', 'useradmin.views.info'),
		(r'^pg/?$', 'useradmin.views.pg'),

)

