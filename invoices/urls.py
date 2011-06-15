# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^/invoice/Faktura-RostiCZ-([0-9]*).pdf$', 'invoices.views.invoice_get'),
	(r'^/next_payment_id/+$', 'invoices.views.next_payment_id'),
	(r'^/items/([0-9]{1,9})/?$', 'invoices.views.items'),
	(r'^/stats/?$', 'invoices.views.stats'),
	(r'^/show/?$', 'invoices.views.show'),
	(r'^/show/([0-9]{1,11})/?$', 'invoices.views.show'),
	(r'^/rm/([0-9]{1,11})/?$', 'invoices.views.rm'),
	(r'^/rm_item/([0-9]{1,11})/?$', 'invoices.views.rm_item'),
	(r'^/invoice/add/?$', 'invoices.views.add_invoice'),
	(r'^/invoice/update/([0-9]{1,11})/?$', 'invoices.views.update_invoice'),
	(r'^/invoice/send/([0-9]{1,11})/?$', 'invoices.views.send_invoice'),
    (r'^/invoice/send/([0-9]{1,11})/(1)/?$', 'invoices.views.send_invoice'),
	(r'^/invoice/payback/([0-9]{1,11})/?$', 'invoices.views.payback'),
	(r'^/invoice/item/add/([0-9]{1,11})/?$', 'invoices.views.add_item'),
	(r'^/invoice/item/update/([0-9]{1,11})/?$', 'invoices.views.update_item'),
)


