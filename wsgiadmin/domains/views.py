# -*- coding: utf-8 -*-

#TODO:Remove, put it in settings


from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render_to_response,get_object_or_404,get_list_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail
from django.db import IntegrityError
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from wsgiadmin.domains.models import *
#from domains.api import *
from wsgiadmin.domains.tools import *

from django.conf import settings

from wsgiadmin.rtools import *

from wsgiadmin.requests.tools import request as push_request
from wsgiadmin.keystore.tools import *

import logging,datetime

domain_api = None#web4u()

@login_required
def show(request,p=1):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	p = int(p)
	
	paginator = Paginator(list(u.domain_set.all()), 10)
	
	if paginator.count == 0:
		page = None
	else:
		page = paginator.page(p)	
		
	return render_to_response('domains.html',
							{
								"domains":page,
								"paginator":paginator,
								"num_page":p,
								"u":u,
								"superuser":superuser,
							    "menu_active": "domains",
							}, context_instance=RequestContext(request))

@login_required
def gen_zone(request,did):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	
	d = get_object_or_404(domain,id=did)
	
	logging.info(_(u"Generuji zónu pro %s")%d.name)

	#Signal
	push_request("bind_add_zone", settings.PRIMARY_DNS, {"domain": d.name, "zone": gen_zone_config(d)}).save()

@login_required
def rm_zone(request,did):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	
	d = get_object_or_404(domain,id=did)
	
	logging.info(_(u"Mažu zóny pro doménu %s")%d.name)

	#Signal
	push_request("bind_rm_zone", settings.PRIMARY_DNS, {"domain": d.name}).save()

@login_required
def gen_conf(request):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	
	logging.info(settings.ROOT+"helpers/update-bind.py"+">"+"/etc/bind/named.local.auto")

	#Signal
	push_request("bind_mod_config", settings.PRIMARY_DNS, {"config": gen_bind_config("pri")}).save()
	push_request("bind_mod_config", settings.SECONDARY_DNS, {"config": gen_bind_config("sec")}).save()

@login_required
@csrf_exempt
def rm(request,did):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	did = int(did)

	d = get_object_or_404(domain,id=did)
	if d.owner == u:
		logging.info(_(u"Mažu doménu %s")%d.name)
		
		rm_zone(request,did)
		d.delete()
		gen_conf(request)
		
		return HttpResponse("Doména vymazána")
	else:
		return HttpResponse("Chyba oprávnění")

@login_required
def add(request):
	"""Zapsání domény, kterou chtějí zákazníci pod svoji správou.
	"""
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	if request.method == 'POST':
		form = form_registration_request(request.POST)
		if form.is_valid():
			name = form.cleaned_data["domain"]
			try:
				instance = domain()
				instance.name = name
				instance.owner = u
				instance.save()

				if settings.PRIMARY_DNS and settings.SECONDARY_DNS and (instance.ipv4 or instance.ipv6):
					gen_zone(request,instance.id)
					gen_conf(request)
				
			except IntegrityError:
				return HttpResponseRedirect(reverse("useradmin.views.error"))
				
			logging.info(_(u"Přidána doména %s")%name)
				
			message = _(u"Nová doména %s přidána")%name
			send_mail('Byla přidána nová doména: '+name,message,settings.EMAIL_FROM,[x[1] for x in settings.ADMINS],fail_silently=False)
				
			return HttpResponseRedirect(reverse("domains.views.show"))
	else:
		form = form_registration_request()
		
	return render_to_response('universal.html',
							{
								"form":form,
								"title":_(u"Přidání domény"),
								"submit":_(u"Přidat doménu do databáze"),
								"action":reverse("domains.views.add"),
								"u":u,
								"superuser":superuser,
							    "menu_active": "domains",
							},
	                        context_instance=RequestContext(request)
						)
	

@login_required
def registration(request):
	"""Registrace nové domény
	"""
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	next_step = False
	valid = ""

	if request.method == 'POST':
		form = form_registration_request_years(request.POST)
		if form.is_valid():
			name = form.cleaned_data["domain"]
			if "years" in form.cleaned_data:
				years = form.cleaned_data["years"]
			else:
				years = 0
			if "passwd" in form.cleaned_data:
				passwd = form.cleaned_data["passwd"]
			else:
				passwd = ""
			
			if name:
				try:
					if domain_api.find(name):
						valid = _(u"Doména je volná")
						next_step = True
					else:
						valid = _(u"Doména je obsazená")
				except SOAPpy.Types.faultType:
					valid = _(u"Při vykonávání požadavku došlo k chybě, zkuste to prosím znovu.")

			instance = registration_request()

			if next_step:
				instance.kind = "registration"
			else:
				instance.kind = "transfer"

			instance.name = name
			instance.user = u
			instance.passwd = passwd
			instance.ip = request.META["REMOTE_ADDR"]
			if "REMOTE_HOST" in request.META:
				instance.hostname = request.META["REMOTE_HOST"]
			else:
				instance.hostname = request.META["REMOTE_ADDR"]
			instance.years = years

			instance.save()
			
			logging.info(_(u"Požadavek na registraci domény %s")%instance.name)
			
			message = _(u"Požadavek na registraci/transfer nové domény %s")%name
			send_mail(_('Požadavek na registraci/transfer nové domény ')+name,message,settings.EMAIL_FROM,[x[1] for x in settings.ADMINS],fail_silently=False)
				
			return HttpResponseRedirect(reverse("domains.views.show"))
	else:
		form = form_registration_request_years()
		
	return render_to_response('universal.html',
							{
								"form":form,
								"title":_(u"Registrace domény"),
								"valid":valid,
								"next_step":next_step,
								"submit":_(u"Registrovat"),
								"action":reverse("domains.views.registration"),
								"u":u,
								"superuser":superuser,
							    "menu_active": "domains",
							},
	                        context_instance=RequestContext(request)
						)

@login_required
def check(request):
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	valid = ""
	next_step = False

	if request.method == 'POST':
		form = form_registration_request_years(request.POST)
		
		if form.is_valid():
			name = form.cleaned_data["domain"]
			logging.info(_(u"Kontroluji dostupnost domény %s")%name)
			
			if name:
				try:
					if domain_api.find(name):
						valid = _(u"Doména je volná")
						next_step = True
					else:
						valid = _(u"Doména je obsazená")
				except SOAPpy.Types.faultType:
					valid = _(u"Při vykonávání požadavku došlo k chybě, zkuste to prosím znovu.")
			
			if next_step:
				return render_to_response('universal.html',
							{
								"form":form,
								"valid":valid,
								"next_step":next_step,
								"title":_(u"Registrace domény"),
								"submit":_(u"Registrovat doménu"),
								"action":reverse("domains.views.registration"),
								"u":u,
								"superuser":superuser,
							    "menu_active": "domains",
								},
				                context_instance=RequestContext(request)
							)
			else:
				return render_to_response('universal.html',
							{
								"form":form,
								"valid":valid,
								"next_step":next_step,
								"title":_(u"Přesunutí domény na NS servery Roští.cz"),
								"submit":_(u"Přesunout doménu"),
								"action":reverse("domains.views.registration"),
								"u":u,
								"superuser":superuser,
							    "menu_active": "domains",
								},
				                context_instance=RequestContext(request)
							)
	else:
		form = form_registration_request()
		
	return render_to_response('universal.html',
							{
								"form":form,
								"valid":valid,
								"next_step":next_step,
								"title":_(u"Registrace domény"),
								"submit":_(u"Ověřit"),
								"action":reverse("domains.views.check"),
								"u":u,
								"superuser":superuser,
							    "menu_active": "domains",
							},
	                        context_instance=RequestContext(request)
						)
