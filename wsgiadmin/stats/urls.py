from django.conf.urls.defaults import *
from wsgiadmin.stats.views import CreditView

urlpatterns = patterns('',
    url(r"^$", CreditView.as_view(), name="credit"),
)
