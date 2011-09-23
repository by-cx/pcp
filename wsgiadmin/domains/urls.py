from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.domains.views',
    (r'^add/$', 'add'),
    (r'^show/$', 'show'),
    (r'^show/([0-9]{1,11})/$', 'show'),
    (r'^rm/([0-9]{1,11})/$', 'rm'),
)
