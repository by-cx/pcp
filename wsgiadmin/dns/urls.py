from django.conf.urls.defaults import *
from wsgiadmin.dns.views import DomainsListView, EditorView, DomainCreateView

urlpatterns = patterns('',
    url(r'^list/$', DomainsListView.as_view(), name="dns_list"),
    url(r'^editor/(?P<pk>\d+)/$', EditorView.as_view(), name="dns_editor"),
    url(r'^editor/(?P<pk>\d+)/(?P<record_pk>\d+)/$', EditorView.as_view(), name="dns_editor"),
    url(r'^create/$', DomainCreateView.as_view(), name="dns_create"),
    url(r'^record/rm/$', 'wsgiadmin.dns.views.rm_record', name="dns_rm_record"),
)
