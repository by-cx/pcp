from django.contrib import admin
from wsgiadmin.virt.models import VirtMachine


class VirtMachineAdmin(admin.ModelAdmin):
    list_display = ("created", "name", "user", "server", )
    list_display_links = ("name", )
    ordering = ['name']


admin.site.register(VirtMachine, VirtMachineAdmin)
