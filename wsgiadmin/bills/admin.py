# -*- coding: utf-8 -*-
from bills.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class bill_admin(admin.ModelAdmin):
	list_display = ("pub_date","price","info","processed","user",)
	list_display_links = ['pub_date']

class service_admin(admin.ModelAdmin):
	list_display = ("info","price","every","user",)
	list_display_links = ('info',)
		
class income_admin(admin.ModelAdmin):
	list_display = ("pub_date","user","cash", "note",)
	list_display_links = ('pub_date',)

admin.site.register(income,income_admin)
admin.site.register(bill,bill_admin)
admin.site.register(service,service_admin)
