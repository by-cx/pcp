# -*- coding: utf-8 -*-
from wsgiadmin.keystore.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class admin_store(admin.ModelAdmin):
	list_display = ("key","value","date_read","date_write")
	list_display_links = ("key",)
	list_filter = ('key',)

admin.site.register(store,admin_store)
