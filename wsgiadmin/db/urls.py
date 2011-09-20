from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.db.views',
    url(r'^add/(?P<dbtype>\w+)/$', 'add', name='db_add'),
    url(r'^show/(?P<dbtype>\w+)/(?P<page>\d+)/$', 'show'),
    url(r'^show/(?P<dbtype>\w+)/$', 'show'),
    url(r'^show/$', 'show'),
    url(r'^rm/([a-z0-9\_\-]*)/$', 'rm'),
    url(r'^passwd/([a-zA-Z0-9\_\-]*)/', 'passwd'),
)
