from django.contrib import admin
from wsgiadmin.stats.models import Credit, TransId, Record

admin.site.register(Credit)
admin.site.register(Record)
admin.site.register(TransId)
