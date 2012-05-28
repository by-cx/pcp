from django.conf.urls.defaults import *
from wsgiadmin.emails.views import mailbox_remove, alias_remove, MailboxListView, EmailAliasListView, addRedirect, addBox

urlpatterns = patterns('wsgiadmin.emails.views',
    url(r'^boxes/$', MailboxListView.as_view(),  name='mailbox_list'),
    url(r'^add_box/$', addBox, name='add_mailbox'),
    url(r'^remove_box/$', mailbox_remove, name='mailbox_remove'),
    (r'^change_passwd_box/([0-9]*)/$', 'changePasswdBox'),

    url(r'^redirects/$', EmailAliasListView.as_view(), name='redirect_list'),
    url(r'^add_redirect/$', addRedirect, name='add_redirect'),
    (r'^change_redirect/([0-9]*)/$', 'changeRedirect'),
    url(r'^removeRedirect/$', alias_remove, name='alias_remove'),
)
