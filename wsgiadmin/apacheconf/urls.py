from django.conf.urls.defaults import *
from wsgiadmin.apacheconf.views import *


urlpatterns = patterns('wsgiadmin.apacheconf.views',
    (r'^sites/?$', 'apache'),
    (r'^sites/([0-9]{1,10})/?$', 'apache'),
    url(r'^addStatic/([0-9]+)/?$', add_static, name="add_static"),
    url(r'^updateStatic/([0-9]+)/?$', update_static, name="update_static"),
    (r'^updateWsgi/([0-9]+)/?$', 'update_wsgi'),
    (r'^removeSite/([0-9]+)/?$', 'remove_site'),
    (r'^reload/([0-9]+)/?$', 'reload'),
    (r'^restart/([0-9]+)/?$', 'restart'),
    (r'^addWsgi/?$', 'add_wsgi'),
    url('^refresh_wsgi/?$', refresh_wsgi, name="refresh_wsgi"),
    url('^refresh_venv/?$', refresh_venv, name="refresh_venv"),
    url('^refresh_userdirs/?$', refresh_userdirs, name="refresh_userdirs"),

)
