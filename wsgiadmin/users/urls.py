from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.users.views',
    (r'^show/$', 'show'),
    (r'^show/([0-9]{1,11})/?$', 'show'),
    (r'^rm/([0-9]{1,11})/?$', 'rm'),
    (r'^add/?$', 'add'),
    (r'^ssh_passwd/?$', 'ssh_passwd'),
    (r'^install/([0-9]{1,11})/', 'install'),
    (r'^update/([0-9]{1,11})/?$', 'update'),
    (r'^update/switch/user/([0-9]{1,11})/([0-9]{1,11})/?$', 'switch_to_user'),
    (r'^update/switch/admin/([0-9]{1,11})/?$', 'switch_to_admin'),
)
