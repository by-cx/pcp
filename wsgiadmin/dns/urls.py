from django.conf.urls.defaults import *
from wsgiadmin.dns.views import DomainsListView, EditorView, DomainCreateView, DomainUpdateView

urlpatterns = patterns('',
    url(r'^list/$', DomainsListView.as_view(), name="dns_list"),
    url(r'^update/(?P<pk>\d+)/$', DomainUpdateView.as_view(), name="dns_domain_update"),
    url(r'^editor/(?P<pk>\d+)/$', EditorView.as_view(), name="dns_editor"),
    url(r'^editor/(?P<pk>\d+)/(?P<record_pk>\d+)/$', EditorView.as_view(), name="dns_editor"),
    url(r'^create/$', DomainCreateView.as_view(), name="dns_create"),
    url(r'^rm/$', 'wsgiadmin.dns.views.rm_domain', name="dns_rm_domain"),
    url(r'^record/rm/$', 'wsgiadmin.dns.views.rm_record', name="dns_rm_record"),
    url(r'^record/order/(?P<domain_pk>\d+)/$', 'wsgiadmin.dns.views.record_order', name="dns_record_order"),
)
