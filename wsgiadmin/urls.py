from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

from django.conf import settings

urlpatterns = patterns('',
	(r'^django-admin/', include(admin.site.urls)),
	(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/m/favicon.ico'}),
	url(r'^m/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ROOT+'m', 'show_indexes': True}),
	#url(r'^m/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
	(r'^invoices', include('wsgiadmin.invoices.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
)

if 'rosetta' in settings.INSTALLED_APPS:
	urlpatterns += patterns('',
		url(r'^rosetta/', include('rosetta.urls')),
	)

urlpatterns += patterns('',
    (r'^new', direct_to_template, {'template': 'new.html'}),
	(r'^', include('wsgiadmin.useradmin.urls')),
)
