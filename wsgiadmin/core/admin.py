from django.contrib import admin
from wsgiadmin.core.models import Server, Capability


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "ip", "ssh", "capabilities_str", "libvirt_url", )
    list_display_links = ("name", )
    ordering = ['name']


admin.site.register(Server, ServerAdmin)
admin.site.register(Capability)
