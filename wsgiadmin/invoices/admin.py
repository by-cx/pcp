# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.invoices.models import *

class invoiceAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'name', 'total', 'date_exposure', 'date_payback', 'paytype', 'sended', 'payed', 'downloadLink')
    list_display_links = ['payment_id', 'name']

    class Media:
        js = ("/m/js/jquery-1.3.2.min.js", "/m/js/jquery.url.packed.js", "/m/js/invoices_admin.js")

admin.site.register(invoice, invoiceAdmin)
admin.site.register(item)
