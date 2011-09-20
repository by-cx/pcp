from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.apacheconf.models import UserSite

class site_admin(admin.ModelAdmin):
    list_display = ("server_name", "pub_date", "documentRoot", "removed")
    list_display_links = ("server_name",)

admin.site.register(UserSite, site_admin)
