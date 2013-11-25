from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from wsgiadmin.virt.views import VirtListView, VirtCreateView, VirtSummaryView, VirtNewView

urlpatterns = patterns('',
    url(r'^new/$', VirtNewView.as_view(), name="virt_new"),
    url(r'^list/$', VirtListView.as_view(), name="virt_list"),
    url(r'^add/$', VirtNewView.as_view(), name="virt_new"),
    url(r'^create/(?P<variant_pk>\d+)/$', VirtCreateView.as_view(), name="virt_create"),
    url(r'^summary/(?P<pk>\d+)/$', VirtSummaryView.as_view(), name="virt_summary"),
    url(r'^change_state/(?P<pk>\d+)/(?P<state>\w+)/$', "wsgiadmin.virt.views.virt_state_changer", name="virt_state"),
    url(r'^backend_install/(?P<pk>\d+)/$', "wsgiadmin.virt.views.backend_install", name="virt_backend_install"),
)
