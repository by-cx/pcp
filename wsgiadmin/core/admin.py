from django.contrib import admin
from wsgiadmin.core.models import Server


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "ip", "python", "php", "mail", "virt", "ssh", "libvirt_url", )
    list_display_links = ("name", )
    ordering = ['name']


admin.site.register(Server, ServerAdmin)
