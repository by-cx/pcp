from django.contrib import admin

from wsgiadmin.apacheconf.models import UserSite

class site_admin(admin.ModelAdmin):
    list_display = ("main_domain", "pub_date", "document_root")
    list_display_links = ("main_domain",)

admin.site.register(UserSite, site_admin)
