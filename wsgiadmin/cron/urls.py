from django.conf.urls.defaults import *
from wsgiadmin.cron.forms import FormCron
from wsgiadmin.cron.views import CronListView, CronUpdateView, CronCreateView

urlpatterns = patterns('wsgiadmin.cron.views',
    url(r'^list/$', CronListView.as_view(), name='cron_list'),
    url(r'^remove/$', "remove_cron", name="remove_cron"),
    url(r'^create/$', CronCreateView.as_view(), name="create_cron"),
    url(r'^update/(?P<pk>\d+)/$', CronUpdateView.as_view(), name="update_cron"),
)