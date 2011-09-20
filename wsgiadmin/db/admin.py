from django.contrib import admin
from wsgiadmin.db.models import PGSQL, MySQLDB

class MySQLAdmin(admin.ModelAdmin):
    list_display = ('dbname', 'owner')
    list_display_links = ['dbname']


class PGAdmin(admin.ModelAdmin):
    list_display = ('dbname', 'owner')
    list_display_links = ['dbname']

admin.site.register(PGSQL, PGAdmin)
admin.site.register(MySQLDB, MySQLAdmin)
