from django.contrib import admin
from wsgiadmin.core.models import Server, Capability, CommandLog, PythonInterpreter


class CommandLogAdmin(admin.ModelAdmin):
    list_display = ("date", "server", "command", "result_stdout", "result_stderr", "status_code", "processed", )
    list_display_links = ("date", )
    ordering = ['-date']


class PythonInterpreterInline(admin.TabularInline):
    model = PythonInterpreter


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "ip", "ssh", "capabilities_str", "libvirt_url", )
    list_display_links = ("name", )
    ordering = ['name']
    inlines = [
        PythonInterpreterInline,
    ]


admin.site.register(CommandLog, CommandLogAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Capability)
