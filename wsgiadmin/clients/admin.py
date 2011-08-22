# -*- coding: utf-8 -*-
from wsgiadmin.clients.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class machine_admin(admin.ModelAdmin):
	list_display = ('name','domain',"ip")
	list_display_links = ['name']

class address_admin(admin.ModelAdmin):
	list_display = ('residency_name','residency_street','residency_city','residency_city_num')
	list_display_links = ['residency_name']
#	list_filter = ['pub_date']
	fieldsets = (
		("Základní", {
			'fields': ('company','note')
		}),
		(_(u"Sídlo"), {
			'fields': ('residency_name','residency_street','residency_city','residency_city_num','residency_ic','residency_dic','residency_email','residency_phone')
		}),
		(_(u"Fakturační adresa"), {
			'classes': ('collapse',),
			'fields': ('different','invoice_name','invoice_street','invoice_city','invoice_city_num','invoice_email','invoice_phone')
		}),
	)

admin.site.register(address,address_admin)
admin.site.register(parms)
admin.site.register(machine,machine_admin)

