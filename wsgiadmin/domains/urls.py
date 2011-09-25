from django.conf.urls.defaults import *
from wsgiadmin.domains.views import *

urlpatterns = patterns('wsgiadmin.domains.views',
    (r'^add/$', 'add'),
    url(r'^show/$', DomainsListView.as_view(), name='domains_list'),
    url(r'^rm/$', rm, name='domain_remove'),
)
