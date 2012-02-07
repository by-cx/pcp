from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.useradmin.views',
    url(r'^$', 'info'),
    url(r'^reg/$', 'reg', name="registration"),
    url(r'^reg-ok/$', 'regok'),
    url(r'^change_passwd/$', 'change_passwd'),
    url(r'^ok/$', 'ok'),
    url(r'^info/$', 'info'),
    url(r'^master/$', 'master', name="master"),
    url(r'^master/app_copy/$', 'app_copy', name="app_copy"),
    url(r'^requests/$', 'requests'),
)

urlpatterns += patterns('',
    url(r'^commit/$', 'wsgiadmin.requests.views.commit'),
    url(r'^domains/', include('wsgiadmin.domains.urls')),
    url(r'^ftp/', include('wsgiadmin.ftps.urls')),
    url(r'^email/', include('wsgiadmin.emails.urls')),
    url(r'^apache/', include('wsgiadmin.apacheconf.urls')),
    url(r'^cron/', include('wsgiadmin.cron.urls')),
    url(r'^db/', include('wsgiadmin.db.urls')),
    url(r'^credit/', include('wsgiadmin.stats.urls')),
    url(r'^users/', include('wsgiadmin.users.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}, name="logout"),
)
