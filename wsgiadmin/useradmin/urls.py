from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.useradmin.views',
    (r'^/?$', 'info'),
    (r'^reg/$', 'reg'),
    (r'^reg-ok/$', 'regok'),
    (r'^change_passwd/$', 'change_passwd'),
    (r'^ok/$', 'ok'),
    (r'^info/$', 'info'),
    (r'^master/$', 'master'),
    (r'^requests/$', 'requests'),   
)

urlpatterns += patterns('',
    (r'^commit/$', 'wsgiadmin.requests.views.commit'),
    (r'^domains/', include('wsgiadmin.domains.urls')),
    (r'^bills/', include('wsgiadmin.bills.urls')),
    (r'^ftp/', include('wsgiadmin.ftps.urls')),
    (r'^email/', include('wsgiadmin.emails.urls')),
    (r'^apache/', include('wsgiadmin.apacheconf.urls')),
    (r'^db/', include('wsgiadmin.db.urls')),
    (r'^users/', include('wsgiadmin.users.urls')),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login_reg.html'}),
    (r'^logout/?$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}),
)
