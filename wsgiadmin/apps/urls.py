from django.conf.urls.defaults import *
from wsgiadmin.apps.views import AppsListView, AppParametersView, AppDetailView, AppCreateView

urlpatterns = patterns('',
       url(r'^list/$', AppsListView.as_view(), name="apps_list"),
       url(r'^detail/(?P<app_id>\d+)/$', AppDetailView.as_view(), name="app_detail"),
       url(r'^add_static/$', AppCreateView.as_view(app_type="static"), name="app_add_static"),
       url(r'^add_php/$', AppCreateView.as_view(app_type="php"), name="app_add_php"),
       url(r'^add_python/$', AppCreateView.as_view(app_type="python"), name="app_add_python"),
       url(r'^add_native/$', AppCreateView.as_view(app_type="native"), name="app_add_native"),
       url(r'^add_proxy/$', AppCreateView.as_view(app_type="proxy"), name="app_add_proxy"),
       url(r'^set_static/(?P<app_id>\d+)/$', AppParametersView.as_view(app_type="static"), name="app_params_static"),
       url(r'^set_php/(?P<app_id>\d+)/$', AppParametersView.as_view(app_type="php"), name="app_params_php"),
       url(r'^set_uwsgi/(?P<app_id>\d+)/$', AppParametersView.as_view(app_type="python"), name="app_params_python"),
       url(r'^set_native/(?P<app_id>\d+)/$', AppParametersView.as_view(app_type="native"), name="app_params_native"),
       url(r'^set_proxy/(?P<app_id>\d+)/$', AppParametersView.as_view(app_type="proxy"), name="app_params_proxy"),
)
