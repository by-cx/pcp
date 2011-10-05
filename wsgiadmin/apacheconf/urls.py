from django.conf.urls.defaults import *
from wsgiadmin.apacheconf.views import *

urlpatterns = patterns('wsgiadmin.apacheconf.views',
    url(r'^sites/$', AppsListView.as_view(), name='app_list'),
    url(r'^sites/(\d+)/$', AppsListView.as_view(), name='app_list'),
    url(r'^remove_site/$', remove_site, name="remove_site"),
    (r'^reload/([0-9]+)/$', 'reload'),
    (r'^restart/([0-9]+)/$', 'restart'),
    url(r'^refresh_wsgi/$', refresh_wsgi, name="refresh_wsgi"),
    url(r'^refresh_venv/$', refresh_venv, name="refresh_venv"),
    url(r'^refresh_userdirs/$', refresh_userdirs, name="refresh_userdirs"),

    url(r'^app_static/(?P<app_type>\w+)/(?P<app_id>\d+)/$', app_static, name="app_static"),
    url(r'^app_static/(?P<app_type>\w+)/$', app_static, name="app_static"),

    url(r'^app_wsgi/(?P<app_id>\d.*)/$', app_wsgi, name="app_wsgi"),
    url(r'^app_wsgi/$', app_wsgi, name="app_wsgi"),
)
