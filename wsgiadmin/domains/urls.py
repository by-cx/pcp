from django.conf.urls.defaults import *
from wsgiadmin.domains.views import *

urlpatterns = patterns('wsgiadmin.domains.views',
    (r'^add/$', 'add'),
    url(r'^show/$', show, name='domains_list'),
    (r'^show/([0-9]{1,11})/$', 'show'),
    url(r'^rm/$', rm, name='domain_remove'),
)
