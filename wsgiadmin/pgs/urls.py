from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^add/?$', 'wsgiadmin.pgs.views.add'),
    (r'^show/?$', 'wsgiadmin.pgs.views.show'),
    (r'^show/([0-9]{1,11})/?$', 'wsgiadmin.pgs.views.show'),
    (r'^rm/([a-z0-9\_\-]*)/?$', 'wsgiadmin.pgs.views.rm'),
    (r'^passwd/([a-zA-Z0-9\_\-]*)/?', 'wsgiadmin.pgs.views.passwd'),
)
