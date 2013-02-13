from django.contrib import admin
from wsgiadmin.apps.models import Server, App, Db

admin.site.register(Server)
admin.site.register(App)
admin.site.register(Db)
