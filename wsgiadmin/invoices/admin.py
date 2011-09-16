# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.invoices.models import *

class invoiceAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'name', 'total', 'date_exposure', 'date_payback', 'paytype', 'sended', 'payed', 'downloadLink')
    list_display_links = ['payment_id', 'name']
    #	list_filter = ['pub_date']
    #	fieldsets = (
    #		("Základní", {
    #			'fields': ('Username','Password','Company','Note')
    #		}),
    #		("Sídlo", {
    #			'fields': ('Residency_Name','Residency_Street','Residency_City','Residency_City_Num','Residency_IC','Residency_DIC','Residency_Email','Residency_Phone')
    #		}),
    #		('Fakturační adresa', {
    #			'classes': ('collapse',),
    #			'fields': ('Different','Invoice_Name','Invoice_Street','Invoice_City','Invoice_City_Num','Invoice_Email','Invoice_Phone')
    #		}),
    #	)

    class Media:
        js = ("/m/js/jquery-1.3.2.min.js", "/m/js/jquery.url.packed.js", "/m/js/invoices_admin.js")

admin.site.register(invoice, invoiceAdmin)
admin.site.register(item)
