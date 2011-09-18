from django.contrib import admin
from wsgiadmin.mysql.models import mysqldb

class mysqldb_admin(admin.ModelAdmin):
    list_display = ('dbname', 'owner')
    list_display_links = ['dbname']

admin.site.register(mysqldb, mysqldb_admin)
