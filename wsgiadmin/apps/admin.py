from django.contrib import admin
from wsgiadmin.apps.models import Server, App, Log, Db

admin.site.register(Server)
admin.site.register(App)
admin.site.register(Log)
admin.site.register(Db)
