from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^bill/([a-z]*)/([0-9]*)/$', 'wsgiadmin.bills.views.show'),
)

