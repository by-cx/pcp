from django.contrib import admin
from wsgiadmin.old.domains.models import Domain
from wsgiadmin.emails.models import Email, EmailRedirect, Message

class EmailAdmin(admin.ModelAdmin):
    list_display = ("last_modified", "address")
    list_display_links = ("last_modified", "address")
    list_filter = ['last_modified']
    ordering = ['-last_modified']
    fieldsets = (
        (None, {'fields': ("login", "domain", "password")}),
    )

    def __init__(self, *args, **kwargs):
        self.has_delete_permission = self.has_change_permission
        super(EmailAdmin, self).__init__(*args, **kwargs)

    def queryset(self, request):
        qs = super(EmailAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(domain__in=Domain.objects.filter(owner=request.user))

    def save_model(self, request, obj, form, change):
        obj.domain.owner = request.user
        obj.save()

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True

        if request.user.is_superuser:
            return True

        return obj.domain.owner == request.user

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #TODO - find out how does this work
        if db_field.name == "domain" and not request.user.is_supersuper:
            #if request.user.is_superuser: kwargs["queryset"] = Domain.objects.all()
            kwargs["queryset"] = Domain.objects.filter(owner=request.user)
            return db_field.formfield(**kwargs)

        return super(EmailAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class MessageAdmin(admin.ModelAdmin):
    list_display = ("purpose", "subject")

admin.site.register(Email, EmailAdmin)
admin.site.register(EmailRedirect)
admin.site.register(Message, MessageAdmin)
