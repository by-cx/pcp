# -*- coding: utf-8 -*-

import os
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404,get_list_or_404
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as user
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from wsgiadmin.pgs.models import *
from wsgiadmin.pgs.tools import *
from wsgiadmin.pcp.tools import *
from wsgiadmin.keystore.tools import *
from wsgiadmin.requests.tools import request as push_request
from wsgiadmin.useradmin.forms import simple_passwd

from django.conf import settings

@login_required
def show(request,p=1):
	"""
		Vylistování seznamu databází
	"""
	p = int(p)
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	
	dbs = u.pgsql_set.all()

	paginator = Paginator([x.dbname for x in dbs], 10)
	
	if paginator.count == 0:
		page = None
	else:
		page = paginator.page(p)	
		
	return render_to_response('pgs.html',
							{
								"pgs":page,
								"paginator":paginator,
								"num_page":p,
								"u":u,
								"superuser":superuser,
							    "menu_active": "dbs",
							}, context_instance=RequestContext(request))

@login_required
def add(request):
	"""
		Vytvoření databáze
	"""
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	if request.method == 'POST':
		form = form_db(request.POST)
		form.u = u
		if form.is_valid():
			db = u.parms.prefix()+"_"+form.cleaned_data["database"]

			p = pgsql()
			p.dbname = db
			p.owner = u
			p.save()

			push_request("pg_add_db", u.parms.pgsql_machine.ip, {"dbname":db, "dbpass":form.cleaned_data["password"]}).save()

			return HttpResponseRedirect(reverse("pgs.views.show"))
	else:
		form = form_db()
		form.u = u
		
	return render_to_response('universal.html',
							{
								"form":form,
								"title":_(u"Vytvoření Postgresql databáze"),
								"submit":_(u"Vytvořit databázi"),
								"action":reverse("pgs.views.add"),
								"u":u,
								"superuser":superuser,
							    "menu_active": "dbs",
							},
	                        context_instance=RequestContext(request)
						)

@login_required
@csrf_exempt
def rm(request,db):
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	p = u.pgsql_set.filter(dbname=db)

	if p:
		push_request("pg_rm_db", u.parms.pgsql_machine.ip, {"dbname": db}).save()
		p[0].delete()

		return HttpResponse("Databáze vymazána")
	else:
		return HttpResponse("Chyba při vykonávání operace")

@login_required
@csrf_exempt
def passwd(request, db):
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	if request.method == "POST":

		form = simple_passwd(request.POST)

		if form.is_valid():

			p = u.pgsql_set.filter(dbname=db)

			if p:
				push_request("pg_passwd_db", u.parms.pgsql_machine.ip, {"dbname": db, "dbpass": form.cleaned_data["password"]}).save()
				return HttpResponse("OK")
		    
	else:
		form = simple_passwd()

	return render_to_response('simplepasswd.html',
							{
								"form":form,
								"title":_(u"Heslo k pgsql databázi %s")%db,
								"submit":_(u"Změni heslo"),
								"action":reverse("pgs.views.passwd", args=[db]),
								"u":u,
								"superuser":superuser,
							    "menu_active": "dbs",
							},
	                        context_instance=RequestContext(request)
						)


