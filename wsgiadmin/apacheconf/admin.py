# -*- coding: utf-8 -*-
from wsgiadmin.emails.models import *
from wsgiadmin.apacheconf.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class site_admin(admin.ModelAdmin):
	list_display = ("serverName","pub_date","documentRoot","removed")
	list_display_links = ("serverName",)

admin.site.register(site,site_admin)
admin.site.register(wsgi)
admin.site.register(alias)
admin.site.register(custom)
