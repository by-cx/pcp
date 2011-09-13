from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.apacheconf.views',
    (r'^sites/?$', 'apache'),
    (r'^sites/([0-9]{1,10})/?$', 'apache'),
    (r'^addStatic/([0-9]*)/?$', 'add_static'),
    (r'^updateStatic/([0-9]*)/?$', 'update_static'),
    (r'^updateWsgi/([0-9]*)/?$', 'update_wsgi'),
    (r'^removeSite/([0-9]*)/?$', 'remove_site'),
    (r'^reload/([0-9]*)/?$', 'reload'),
    (r'^restart/([0-9]*)/?$', 'restart'),
    (r'^addWsgi/?$', 'add_wsgi'),
)
