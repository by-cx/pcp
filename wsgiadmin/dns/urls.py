from django.conf.urls.defaults import *
from wsgiadmin.dns.views import DomainsListView, EditorView, DomainCreateView

urlpatterns = patterns('',
    url(r'^list/$', DomainsListView.as_view(), name="dns_list"),
    url(r'^editor/(?P<pk>\d+)/$', EditorView.as_view(), name="dns_editor"),
    url(r'^create/$', DomainCreateView.as_view(), name="dns_create"),
)
