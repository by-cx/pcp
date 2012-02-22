# -*- coding: utf-8 -*-
from wsgiadmin.clients.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class machine_admin(admin.ModelAdmin):
    list_display = ('name', 'domain', "ip")
    list_display_links = ['name']

admin.site.register(Parms)
admin.site.register(Machine, machine_admin)
