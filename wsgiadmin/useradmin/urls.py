from django.conf.urls.defaults import *
from wsgiadmin.service.forms import LoginFormHelper
from wsgiadmin.useradmin.views import PasswordView, EmailView

urlpatterns = patterns('wsgiadmin.useradmin.views',
                       url(r'^$', 'info'),
                       url(r'^reg/$', 'reg', name="registration"),
                       url(r'^reg-ok/$', 'regok'),
                       url(r'^change_passwd/$', 'change_passwd'),
                       url(r'^reset_passwd/$', PasswordView.as_view(),
                           name='reset_passwd'),
                       url(r'^ok/$', 'ok'),
                       url(r'^info/$', 'info'),
                       url(r'^master/$', 'master', name="master"),
                       url(r'^master/app_copy/$', 'app_copy', name="app_copy"),
                       url(r'^requests/$', 'requests'),
                       )

urlpatterns += patterns('',
                        url(r'^send_email/$', EmailView.as_view(), name='send_email'),
                        url(r'^commit/$', 'wsgiadmin.old.requests.views.commit'),
                        url(r'^domains/', include('wsgiadmin.old.domains.urls')),
                        url(r'^clients/', include('wsgiadmin.clients.urls')),
                        url(r'^ftp/', include('wsgiadmin.old.ftps.urls')),
                        url(r'^dns/', include('wsgiadmin.dns.urls')),
                        url(r'^email/', include('wsgiadmin.emails.urls')),
                        url(r'^apache/', include('wsgiadmin.old.apacheconf.urls')),
                        url(r'^cron/', include('wsgiadmin.old.cron.urls')),
                        url(r'^db/', include('wsgiadmin.old.db.urls')),
                        url(r'^credit/', include('wsgiadmin.stats.urls')),
                        url(r'^users/', include('wsgiadmin.users.urls')),
                        url(r'^apps/', include('wsgiadmin.apps.urls')),
                        url(r'^vm/', include('wsgiadmin.virt.urls')),
                        url(r'^login/$', 'django.contrib.auth.views.login',
                                {
                                    'template_name': 'login.html',
                                    'extra_context': {
                                        'form_helper': LoginFormHelper(),
                                        'menu_active': 'login',
                                    }
                                },
                            name="login"
                        ),
                        url(r'^logout/$', 'django.contrib.auth.views.logout',
                                {
                                    'template_name': 'logout.html',
                                    'extra_context': {
                                        'form_helper': LoginFormHelper(),
                                    }
                                },
                                name = "logout"
                        ),
)
