from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.emails.views',
    (r'^email_info/$', 'email_info'),
    (r'^boxes/([0-9]{1,10})/$', 'boxes'),
    (r'^boxes/$', 'boxes'),
    (r'^add_box/$', 'addBox'),
    (r'^remove_box/([0-9]*)/$', 'removeBox'),
    (r'^change_passwd_box/([0-9]*)/$', 'changePasswdBox'),
    (r'^redirects/([0-9]{1,10})/$', 'redirects'),
    (r'^redirects/$', 'redirects'),
    (r'^add_redirect/$', 'addRedirect'),
    (r'^change_redirect/([0-9]*)/$', 'changeRedirect'),
    (r'^removeRedirect/([0-9]*)/$', 'removeRedirect'),
)
