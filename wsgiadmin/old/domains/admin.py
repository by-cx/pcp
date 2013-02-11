from django.contrib import admin

from wsgiadmin.old.domains.models import *


class DomainAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "mail", "dns"]
    list_filter = ["owner", "mail", "dns"]


    def __init__(self, model, admin_site):
        self.has_delete_permission = self.has_change_permission
        super(DomainAdmin, self).__init__(model, admin_site)

    def queryset(self, request):
        qs = super(DomainAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(owner=request.user)


    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser:
            return True

        return obj.owner == request.user

admin.site.register(Domain, DomainAdmin)
