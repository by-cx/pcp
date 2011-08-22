# -*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404,get_list_or_404
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as user
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from wsgiadmin.mysql.models import *
from wsgiadmin.mysql.tools import *
from wsgiadmin.keystore.tools import *
from wsgiadmin.clients.models import formPassword
from wsgiadmin.requests.tools import request as push_request
from wsgiadmin.useradmin.forms import simple_passwd

from wsgiadmin.settings import ROOT

@login_required
def show(request,p=1):
	"""
		Vylistování seznamu databází
	"""
	p = int(p)
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	dbs = u.mysqldb_set.all()

	paginator = Paginator([x.dbname for x in dbs], 10)

	if paginator.count == 0:
		page = None
	else:
		page = paginator.page(p)

	return render_to_response('mysql.html',
							{
								"dbs":page,
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

			m = mysqldb()
			m.dbname = db
			m.owner = u
			m.save()

			push_request("my_add_db", u.parms.mysql_machine.ip, {"dbname":db, "dbpass":form.cleaned_data["password"]}).save()

			return HttpResponseRedirect(reverse("mysql.views.show"))
	else:
		form = form_db()
		form.u = u

	return render_to_response('universal.html',
							{
								"form":form,
								"title":_(u"Vytvoření MySQL databáze"),
								"submit":_(u"Vytvořit databázi"),
								"action":reverse("mysql.views.add"),
								"u":u,
								"superuser":superuser,
							    "menu_active": "dbs",
							},
	                        context_instance=RequestContext(request)
						)

@login_required
@csrf_exempt
def passwd(request, db):
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	if request.method == "POST":

		form = simple_passwd(request.POST)

		if form.is_valid():

			if u.mysqldb_set.filter(dbname=db):
				push_request("my_passwd_db", u.parms.mysql_machine.ip, {"dbname": db, "dbpass": form.cleaned_data["password"]}).save()
				return HttpResponse("OK")

	else:
		form = simple_passwd()

	return render_to_response('simplepasswd.html',
							{
								"form":form,
								"title":_(u"Heslo k mysql databázi %s")%db,
								"submit":_(u"Změni heslo"),
								"action":reverse("mysql.views.passwd", args=[db]),
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

	m = u.mysqldb_set.filter(dbname=db)

	if m:
		push_request("my_rm_db", u.parms.mysql_machine.ip, {"dbname": db}).save()
		m[0].delete()

		return HttpResponse("Databáze vymazána")
	else:
		return HttpResponse("Chyba při vykonávání operace")
