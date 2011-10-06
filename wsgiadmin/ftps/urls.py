from django.conf.urls.defaults import *
from wsgiadmin.ftps.views import FTPListView, ftp_upsert, remove_ftp, passwd_ftp

urlpatterns = patterns('',
    url(r'^ftp_upsert/(?P<ftp_id>\d+)/$', ftp_upsert, name='ftp_upsert'),
    url(r'^ftp_upsert/$', ftp_upsert, name='ftp_upsert'),

    url(r'^remove_site/$', remove_ftp, name="ftp_remove"),
    url(r'^passwd/(?P<ftp_id>\d+)/$', passwd_ftp, name='ftp_passwd'),

    url(r'^$', FTPListView.as_view(), name='ftp_list'),
)
