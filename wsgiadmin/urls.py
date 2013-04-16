from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('')

if getattr(settings, 'ENABLE_DEBUG_URLS', False):
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    )

urlpatterns += patterns('',
    url(r'^django-admin/', include(admin.site.urls)),
    url(r'^gopay/', include('gopay4django.urls')),
    url(r'^favicon\.ico$', 'wsgiadmin.tools.redirect_to', {'url': '/static/favicon.ico'}),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

urlpatterns += patterns('',
    url(r'^', include('wsgiadmin.useradmin.urls')),
)
