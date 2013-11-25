from django.conf.urls import patterns, url
from wsgiadmin.clients.views import AddressCreate, AddressUpdate, AddressList

urlpatterns = patterns('',
    url(r'^create/$', AddressCreate.as_view(), name='address_create'),
    url(r'^update/(?P<pk>\d+)/$', AddressUpdate.as_view(), name='address_update'),
    url(r'^delete/(?P<pk>\d+)/$', "wsgiadmin.clients.views.delete_address", name='address_delete'),
    url(r'^list/$', AddressList.as_view(), name='address_list'),
)