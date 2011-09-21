from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.db.views',
    url(r'^add/(?P<dbtype>\w+)/$', 'add', name='db_add'),
    url(r'^show/(?P<dbtype>\w+)/(?P<page>\d+)/$', 'show', name='db_list'),
    url(r'^show/(?P<dbtype>\w+)/$', 'show', name='db_list'),
    url(r'^show/$', 'show'),
    url(r'^rm/(?P<dbtype>\w+)/$', 'rm', name='db_remove'),
    url(r'^passwd/(?P<dbtype>\w+)/(?P<dbname>\w+)/$', 'passwd', name='db_passwd'),
)
