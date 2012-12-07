# -*- coding: utf-8 -*-
from wsgiadmin.clients.models import Parms, Address, Machine
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', "ip")
    list_display_links = ['name']

class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'street', "zip", "city", "phone", "email")
    list_display_links = ['name']

admin.site.register(Parms)
admin.site.register(Address, AddressAdmin)
admin.site.register(Machine, MachineAdmin)
