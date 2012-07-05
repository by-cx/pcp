from django.conf.urls.defaults import *
from wsgiadmin.domains.views import DomainUpdateView, DomainsListView

urlpatterns = patterns('wsgiadmin.domains.views',
    url(r'^add/$', "add", name='domain_add'),
    url(r'^update/(?P<pk>\d+)/$', DomainUpdateView.as_view(), name='domain_update'),
    url(r'^show/$', DomainsListView.as_view(), name='domains_list'),
    url(r'^rm/$', "rm", name='domain_remove'),
    url(r'^subdomains/([0-9]*)/$', "subdomains", name='subdomains'),
    url(r'^subdomains_list/([0-9]*)/$', "subdomains_list", name='subdomains_list'),
)
