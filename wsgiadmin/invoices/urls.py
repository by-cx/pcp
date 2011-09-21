from django.conf.urls.defaults import *

urlpatterns = patterns('wsgiadmin.invoices.views',
    (r'^/invoice/Faktura-RostiCZ-([0-9]*).pdf$', 'invoice_get'),
    (r'^/next_payment_id/+$', 'next_payment_id'),
    (r'^/items/([0-9]{1,9})/$', 'items'),
    (r'^/stats/$', 'stats'),
    (r'^/show/$', 'show'),
    (r'^/show/([0-9]{1,11})/$', 'show'),
    (r'^/rm/([0-9]{1,11})/$', 'rm'),
    (r'^/rm_item/([0-9]{1,11})/$', 'rm_item'),
    (r'^/invoice/add/$', 'add_invoice'),
    (r'^/invoice/update/([0-9]{1,11})/$', 'update_invoice'),
    (r'^/invoice/send/([0-9]{1,11})/$', 'send_invoice'),
    (r'^/invoice/send/([0-9]{1,11})/(1)/$', 'send_invoice'),
    (r'^/invoice/payback/([0-9]{1,11})/$', 'payback'),
    (r'^/invoice/item/add/([0-9]{1,11})/$', 'add_item'),
    (r'^/invoice/item/update/([0-9]{1,11})/$', 'update_item'),
)
