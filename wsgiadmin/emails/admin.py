# -*- coding: utf-8 -*-
from emails.models import *
from domains.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class emailAdmin(admin.ModelAdmin):
	list_display = ("pub_date","address")
	list_display_links = ("pub_date","address")
	list_filter = ['pub_date']
	ordering = ['-pub_date']
	fieldsets = (
		(None, {'fields': ("login","domain","password")}),
	)

	def queryset(self, request):
		qs = super(emailAdmin, self).queryset(request)
		if request.user.is_superuser:
			return qs
		else:
			return qs.filter(domain__in=domain.objects.filter(owner=request.user))
    
	def save_model(self, request, obj, form, change):
		obj.domain.owner = request.user
		obj.save()
    
	def has_change_permission(self, request, obj=None):
		if not obj:
			return True
		if request.user.is_superuser or obj.domain.owner == request.user:
			return True
		else:
			return False
 
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "domain":
			if request.user.is_superuser:
				kwargs["queryset"] = domain.objects.all()
			else:
				kwargs["queryset"] = domain.objects.filter(owner=request.user)
			return db_field.formfield(**kwargs)
		return super(emailAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
   
	has_delete_permission = has_change_permission  


admin.site.register(email,emailAdmin)
admin.site.register(redirect)
