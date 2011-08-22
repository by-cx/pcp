# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from mysql.models import *

class mysqldb_admin(admin.ModelAdmin):
	list_display = ('dbname','owner')
	list_display_links = ['dbname']

admin.site.register(mysqldb,mysqldb_admin)
