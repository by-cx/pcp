from django.conf.urls.defaults import *
from wsgiadmin.supervisor.views import ListProgram, UpdateProgram, CreateProgram

urlpatterns = patterns('',
    url(r'^create/$', CreateProgram.as_view(), name='create_program'),
    url(r'^update/$', UpdateProgram.as_view(), name='update_program'),
    url(r'^show/$', ListProgram.as_view(), name='list_programs'),
    url(r'^rm/$', "wsgiadmin.supervisor.views.rm", name='domain_remove'),
)
