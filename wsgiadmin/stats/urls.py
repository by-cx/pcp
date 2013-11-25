from django.conf.urls import patterns, url
from wsgiadmin.stats.views import CreditView, StatsView, PaymentView, PaymentsView, PaymentDone, PaymentError

urlpatterns = patterns('',
    url(r"^payments/$", PaymentsView.as_view(), name="payments_info"),
    url(r"^payment/(?P<pk>\d+)/$", PaymentView.as_view(), name="payment_info"),
    url(r"^payment/change_address/$", "wsgiadmin.stats.views.change_address", name="payment_address"),
    url(r"^payment/payed/$", "wsgiadmin.stats.views.send_invoice", name="payment_payed"),
    url(r"^payment/done/$", PaymentDone.as_view(), name="payment_done"),
    url(r"^payment/error/$", PaymentError.as_view(), name="payment_error"),
    url(r"^payment/gopay/$", "wsgiadmin.stats.views.create_gopay_payment", name="payment_gopay"),
    url(r"^stats/$", StatsView.as_view(), name="credit_stats"),
    url(r"^$", CreditView.as_view(), name="credit"),
)
