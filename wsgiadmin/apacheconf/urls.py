from django.conf.urls.defaults import *
from wsgiadmin.apacheconf.views import *

urlpatterns = patterns('wsgiadmin.apacheconf.views',
    (r'^sites/$', 'apache'),
    (r'^sites/([0-9]{1,10})/$', 'apache'),
    url(r'^addStatic/([0-9]+)/$', add_static, name="add_static"),
    url(r'^updateStatic/([0-9]+)/$', update_static, name="update_static"),
    url(r'^remove_site/$', remove_site, name="remove_site"),
    (r'^reload/([0-9]+)/$', 'reload'),
    (r'^restart/([0-9]+)/$', 'restart'),
    url(r'^refresh_wsgi/$', refresh_wsgi, name="refresh_wsgi"),
    url(r'^refresh_venv/$', refresh_venv, name="refresh_venv"),
    url(r'^refresh_userdirs/$', refresh_userdirs, name="refresh_userdirs"),
    url(r'^app_wsgi/(\d+)/$', app_wsgi, name="app_wsgi"),
    url(r'^app_wsgi/$', app_wsgi, name="app_wsgi"),
)
