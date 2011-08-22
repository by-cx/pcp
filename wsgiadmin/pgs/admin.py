# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.pgs.models import *

class pgsql_admin(admin.ModelAdmin):
	list_display = ('dbname','owner')
	list_display_links = ['dbname']

admin.site.register(pgsql,pgsql_admin)
