from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.users.views',
    url(r'^show/$', 'show', name="users_list"),
    url(r'^rm/([0-9]{1,11})/$', 'rm', name="user_rm"),
    url(r'^add/$', 'add'),
    url(r'^ssh_passwd/$', 'ssh_passwd'),
    url(r'^install/([0-9]{1,11})/', 'install'),
    url(r'^update/([0-9]{1,11})/$', 'update'),
    url(r'^update/switch/user/([0-9]{1,11})/$', 'switch_to_user', name="switch_to_user"),
    url(r'^update/switch/admin/$', 'switch_to_admin', name="switch_to_admin"),
)
