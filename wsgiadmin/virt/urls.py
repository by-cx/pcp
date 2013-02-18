from django.conf.urls.defaults import patterns, url
from wsgiadmin.virt.views import VirtListView, VirtCreateView

urlpatterns = patterns('',
    url(r'^list/$', VirtListView.as_view(), name="virt_list"),
    url(r'^add/$', VirtCreateView.as_view(), name="virt_create"),
)
