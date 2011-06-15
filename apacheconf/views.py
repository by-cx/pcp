# -*- coding: utf-8 -*-

import logging
from django.core.paginator import Paginator
from django.shortcuts import render_to_response,get_object_or_404
from django.contrib.auth.decorators import login_required
from emails.models import *
from django.core.urlresolvers import reverse
from clients.models import *
from django.http import HttpResponse,HttpResponseRedirect
from requests.tools import request as push_request
from apacheconf.models import *
from ftps.tools import *
from django.utils.translation import ugettext_lazy as _
from apacheconf.tools import gen_vhosts, gen_uwsgi_xml
from django.template.context import RequestContext

info = logging.info

@login_required
def apache(request,p=1):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	p = int(p)

	paginator = Paginator(list(u.site_set.filter(removed=False)), 25)

	if paginator.count == 0:
		page = None
	else:
		page = paginator.page(p)

	return render_to_response("apache.html",
							{
								"sites":page,
								"paginator":paginator,
								"num_page":p,
								"u":u,
								"superuser":superuser,
							    "menu_active": "webapps",
							})

@login_required
def serverNameAliasCheck(request,form,thisSite=None):
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	serverName = form.data["serverName"].strip()
	serverAlias = form.data["serverAlias"]

	domains = [] # domény u aktuální stránky
	usedDomains = [] # Všechny domény použité u aplikací
	errorDomains = []
	domains.append(serverName)

	domains += [domain.strip() for domain in serverAlias.split(" ") if domain]

	#Použití domény
	for site in u.site_set.filter(removed=False):
		if thisSite and thisSite == site:
			continue
		usedDomains.append(site.serverName)
		for domain in site.serverAlias.split(" "):
			if domain:
				usedDomains.append(domain.strip())

	#test vlastnictví
	for domain in domains:
		test = False
		for ownDomain in [d.name for d in u.domain_set.all()]:
			if ownDomain in domain:
				test = True
				break
		if not test:
			errorDomains.append(domain)

	#použité domény
	for domain in domains:
		if domain in usedDomains:
			if not domain in errorDomains: errorDomains.append(domain)

	return errorDomains


@login_required
def addStatic(request,php="0"):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	siteErrors = []

	choices = [(d,d) for d in user_directories(u)]

	if request.method == 'POST':
		form = formStatic(request.POST)
		form.fields["documentRoot"].choices = choices
		siteErrors = serverNameAliasCheck(request,form)
		if not siteErrors and form.is_valid():
			web = site()
			web.serverName = form.cleaned_data["serverName"]
			web.serverAlias = form.cleaned_data["serverAlias"]
			web.documentRoot = form.cleaned_data["documentRoot"]

			if php == "0":
				web.php = False
			else:
				web.php = True
			    
			web.owner = u
			web.save()

			#Signal
			push_request("apache_reload", u.parms.web_machine.ip, {"domain": web.serverName, "user": u.username, "vhosts": gen_vhosts() }).save()

			return HttpResponseRedirect(reverse("apacheconf.views.apache"))
	else:
		form = formStatic()
		form.fields["documentRoot"].choices = choices

	if php == "0": title = _(u"Přidání statického webu")
	else: title = _(u"Přidání webu s podporou PHP")

	return render_to_response('universal.html',
								{
									"siteErrors":siteErrors,
									"form":form,
									"title":title,
									"submit":_(u"Přidat web"),
									"action":reverse("apacheconf.views.addStatic",args=[php]),
									"u":u,
									"superuser":superuser,
								    "menu_active": "webapps",
								},
	                            context_instance=RequestContext(request)
							)

@login_required
def updateStatic(request,sid):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	siteErrors = []
	sid = int(sid)

	s = get_object_or_404(site,id=sid)
	choices = [(d,d) for d in user_directories(u)]

	if request.method == 'POST':
		form = formStatic(request.POST)
		form.fields["documentRoot"].choices = choices
		siteErrors = serverNameAliasCheck(request,form,s)
		if not siteErrors and form.is_valid():
			s.serverName = form.cleaned_data["serverName"]
			s.serverAlias = form.cleaned_data["serverAlias"]
			s.documentRoot = form.cleaned_data["documentRoot"]
			s.save()

			#Signal
			push_request("apache_reload", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "vhosts": gen_vhosts()}).save()

			return HttpResponseRedirect(reverse("apacheconf.views.apache"))
	else:
		form = formStatic(initial={"serverName":s.serverName,"serverAlias":s.serverAlias,"documentRoot":s.documentRoot})
		form.fields["documentRoot"].choices = choices

	return render_to_response('universal.html',
								{
									"siteErrors":siteErrors,
									"form":form,
									"title":_(u"Úprava statického webu"),
									"submit":_(u"Upravit web"),
									"action":reverse("apacheconf.views.updateStatic",args=[s.id]),
									"u":u,
									"superuser":superuser,
								    "menu_active": "webapps",
								},
	                            context_instance=RequestContext(request)
							)

@login_required
def removeSite(request,sid):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	sid = int(sid)

	s = get_object_or_404(site,id=sid)
	if s.owner == u:
		s.removed = True
		s.end_date = datetime.date.today()
		s.save()

		#Signal
		push_request("apache_reload", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "vhosts": gen_vhosts()}).save()
		push_request("uwsgi_config", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "config": gen_uwsgi_xml() }).save()

	return HttpResponse("Stránka vymazána")

@login_required
def addWsgi(request):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	siteErrors = []

	rr = request_raw(u.parms.web_machine.ip)
	wsgis = rr.run(("/usr/bin/find %s -maxdepth 5 -name *.wsgi" % u.parms.home))["stdout"]
	if wsgis:
		wsgis = wsgis.split("\n")
	else:
		wsgis = []

	choices = [("",_(u"Nevybráno"))]+[(x.strip(),x.strip()) for x in wsgis if x]

	virtualenvs = rr.run(("/usr/bin/find %s/virtualenvs/ -maxdepth 1 -type d" % u.parms.home))["stdout"].split("\n")
	virtualenvs_choices = [(x[len(u.parms.home+"/virtualenvs/"):],x[len(u.parms.home+"/virtualenvs/"):]) for x in virtualenvs if x[len(u.parms.home+"/virtualenvs/"):]]

	if request.method == 'POST':
		form = formWsgi(request.POST)
		form.fields["script"].choices = choices
		form.fields["virtualenv"].choices = virtualenvs_choices
		siteErrors = serverNameAliasCheck(request,form)
		if not siteErrors and form.is_valid():
			web = site()
			web.serverName = form.cleaned_data["serverName"]
			web.serverAlias = form.cleaned_data["serverAlias"]
			web.owner = u
			web.save()

			webWsgi = wsgi()
			webWsgi.virtualenv = form.cleaned_data["virtualenv"]
			webWsgi.static = form.cleaned_data["static"]
			webWsgi.python_path = form.cleaned_data["python_path"]
			webWsgi.script = form.cleaned_data["script"]
			webWsgi.allow_ips = form.cleaned_data["allow_ips"]
			webWsgi.site = web
			webWsgi.save()

			#Signal
			push_request("apache_reload", u.parms.web_machine.ip, {"domain": web.serverName, "user": u.username, "vhosts": gen_vhosts()}).save()
			if webWsgi.uwsgi:
				push_request("uwsgi_config", u.parms.web_machine.ip, {"domain": web.serverName, "user": u.username, "config": gen_uwsgi_xml() }).save()
				push_request("uwsgi_start", u.parms.web_machine.ip, {"web_id": webWsgi.id, "domain": web.serverName, "user": u.username, "config": gen_uwsgi_xml() }).save()

			return HttpResponseRedirect(reverse("apacheconf.views.apache"))
	else:
		form = formWsgi()
		form.fields["script"].choices = choices
		form.fields["virtualenv"].choices = virtualenvs_choices

	return render_to_response('universal.html',
								{
									"siteErrors":siteErrors,
									"form":form,
									"title":_(u"Přidání WSGI aplikace"),
									"submit":_(u"Přidat WSGI aplikaci"),
									"action":reverse("apacheconf.views.addWsgi"),
									"u":u,
									"superuser":superuser,
								    "menu_active": "webapps",
								},
	                            context_instance=RequestContext(request)
							)

@login_required
def updateWsgi(request,sid):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	siteErrors = []

	rr = request_raw(u.parms.web_machine.ip)
	wsgis = rr.run(("/usr/bin/find %s -maxdepth 5 -name *.wsgi" % u.parms.home))["stdout"]
	if wsgis:
		wsgis = wsgis.split("\n")
	else:
		wsgis = []
	choices = [("",_(u"Nevybráno"))]+[(x.strip(),x.strip()) for x in wsgis if x]

	virtualenvs = rr.run(("/usr/bin/find %s/virtualenvs/ -maxdepth 1 -type d" % u.parms.home))["stdout"].split("\n")
	virtualenvs_choices = [(x[len(u.parms.home+"/virtualenvs/"):],x[len(u.parms.home+"/virtualenvs/"):]) for x in virtualenvs if x[len(u.parms.home+"/virtualenvs/"):]]

	#TODO:make secure update
	sid = int(sid)
	s = get_object_or_404(site,id=sid)

	if request.method == 'POST':
		form = formWsgi(request.POST)
		form.fields["script"].choices = choices
		form.fields["virtualenv"].choices = virtualenvs_choices
		siteErrors = serverNameAliasCheck(request,form,s)
		if not siteErrors and form.is_valid():
			s.serverName = form.cleaned_data["serverName"]
			s.serverAlias = form.cleaned_data["serverAlias"]
			s.save()

			s.wsgi.virtualenv = form.cleaned_data["virtualenv"]
			s.wsgi.static = form.cleaned_data["static"]
			s.wsgi.script = form.cleaned_data["script"]
			s.wsgi.python_path = form.cleaned_data["python_path"]
			s.wsgi.allow_ips = form.cleaned_data["allow_ips"]
			s.wsgi.save()

			#Signal
			if s.wsgi.uwsgi:
				push_request("uwsgi_config", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "config": gen_uwsgi_xml() }).save()
				push_request("uwsgi_restart", u.parms.web_machine.ip, {"web_id": s.id, "domain": s.serverName, "user": u.username, "config": gen_uwsgi_xml() }).save()
				push_request("apache_reload", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "vhosts": gen_vhosts()}).save()
			else:
				push_request("apache_reload", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "vhosts": gen_vhosts()}).save()

			return HttpResponseRedirect(reverse("apacheconf.views.apache"))
	else:
		form = formWsgi(initial={"serverName":s.serverName,"serverAlias":s.serverAlias,"script":s.wsgi.script,"allow_ips":s.wsgi.allow_ips,"static": s.wsgi.static,"virtualenv": s.wsgi.virtualenv, "python_path": s.wsgi.python_path})
		form.fields["script"].choices = choices
		form.fields["virtualenv"].choices = virtualenvs_choices

	return render_to_response('universal.html',
								{
									"siteErrors":siteErrors,
									"form":form,
									"title":_(u"Upravení WSGI aplikace"),
									"submit":_(u"Upravit WSGI aplikaci"),
									"action":reverse("apacheconf.views.updateWsgi",args=[s.id]),
									"u":u,
									"superuser":superuser,
								    "menu_active": "webapps",
								},
	                            context_instance=RequestContext(request)
							)
@login_required
def reload(request, sid):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	
	sid = int(sid)
	s = get_object_or_404(site,id=sid)

	#Signal
	if s.wsgi.uwsgi:
		push_request("uwsgi_config", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "config": gen_uwsgi_xml() }).save()
		push_request("uwsgi_reload", u.parms.web_machine.ip, {"web_id": s.wsgi.id, "domain": s.serverName, "user": u.username, "config": gen_uwsgi_xml() }).save()
	else:
		push_request("apache_reload", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "vhosts": gen_vhosts()}).save()
	
	return HttpResponseRedirect(reverse("apacheconf.views.apache"))

@login_required
def restart(request, sid):
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	sid = int(sid)
	s = get_object_or_404(site,id=sid)

	#Signal
	if s.wsgi.uwsgi:
		push_request("uwsgi_config", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "config": gen_uwsgi_xml() }).save()
		push_request("uwsgi_restart", u.parms.web_machine.ip, {"web_id": s.wsgi.id, "domain": s.serverName, "user": u.username, "config": gen_uwsgi_xml() }).save()
	else:
		push_request("apache_restart", u.parms.web_machine.ip, {"domain": s.serverName, "user": u.username, "vhosts": gen_vhosts()}).save()

	return HttpResponseRedirect(reverse("apacheconf.views.apache"))
