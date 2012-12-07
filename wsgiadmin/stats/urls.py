from django.conf.urls.defaults import patterns, url
from wsgiadmin.stats.views import CreditView, StatsView, PaymentView, PaymentsView

urlpatterns = patterns('',
    url(r"^payments/$", PaymentsView.as_view(), name="payments_info"),
    url(r"^payment/(?P<pk>\d+)/$", PaymentView.as_view(), name="payment_info"),
    url(r"^payment/change_address/$", "wsgiadmin.stats.views.change_address", name="payment_address"),
    url(r"^stats/$", StatsView.as_view(), name="credit_stats"),
    url(r"^$", CreditView.as_view(), name="credit"),
)
