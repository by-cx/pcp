# -*- coding: utf-8 -*-
from domains.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class domainAdmin(admin.ModelAdmin):
	list_display = ["name","owner","mail","dns"]
	list_filter = ["owner","mail","dns"]

	def queryset(self, request):
		qs = super(domainAdmin, self).queryset(request)
		if request.user.is_superuser:
			return qs
		else:
			return qs.filter(owner=request.user)
    
	def save_model(self, request, obj, form, change):
		#obj.owner = request.user
		obj.save()
    
	def has_change_permission(self, request, obj=None):
		if not obj:
			return True
		if request.user.is_superuser or obj.owner == request.user:
			return True
		else:
			return False
    
	has_delete_permission = has_change_permission  

admin.site.register(domain,domainAdmin)
admin.site.register(registration_request)
