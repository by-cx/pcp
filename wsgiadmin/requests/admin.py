from django.contrib import admin
from wsgiadmin.requests.models import Request

class RequestAdmin(admin.ModelAdmin):
    list_display = ('add_date', 'done_date', 'machine', 'done', 'action')
    list_display_links = ['add_date']
    list_filter = ['action']

admin.site.register(Request, RequestAdmin)
