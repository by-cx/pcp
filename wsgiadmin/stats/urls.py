from django.conf.urls.defaults import *
from wsgiadmin.stats.views import CreditView, StatsView

urlpatterns = patterns('',
    url(r"^stats/$", StatsView.as_view(), name="credit_stats"),
    url(r"^$", CreditView.as_view(), name="credit"),
)
