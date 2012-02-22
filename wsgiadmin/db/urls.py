from django.conf.urls.defaults import *
from wsgiadmin.db.views import DatabasesListView

urlpatterns = patterns('wsgiadmin.db.views',
    url(r'^add/(?P<dbtype>\w+)/$', 'add', name='db_add'),
    url(r'^show/(?P<dbtype>\w+)/$', DatabasesListView.as_view(), name='db_list'),
    url(r'^show/$', DatabasesListView.as_view(), name='db_list'),
    url(r'^rm/(?P<dbtype>\w+)/$', 'rm', name='db_remove'),
    url(r'^passwd/(?P<dbtype>\w+)/(?P<dbname>\w+)/$', 'passwd', name='db_passwd'),
)
