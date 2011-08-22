# -*- coding: utf-8 -*-

import os
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404,get_list_or_404
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as user

#from users.models import *
from keystore.tools import *
from requests.tools import request_raw

from rtools import *
#from mysql.tools import *

from useradmin.views import info

class user_middleware:
	"""
		Stará se vyplnění keystore cache pro konfiguraci systému.
	"""

	def process_view(self, request, view_func, view_args, view_kwargs):
		u = request.user

		if not u.is_authenticated():# or view_func != info:
			return None

		if u.username+":passwd" in klist():
			return None

		rr = request_raw(u.parms.web_machine.ip)
		data = rr.run("cat /etc/passwd")["stdout"]
		users = []

		if data:
			for x in [x.split(":") for x in data.split("\n") if x]:
				users.append(x[0])
		
		if u.username in users:
			kset(u.username+":passwd",u.parms.machine.name)

		return None

