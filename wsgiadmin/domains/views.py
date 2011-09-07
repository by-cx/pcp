# -*- coding: utf-8 -*-

#TODO:Remove, put it in settings


from django.core.paginator import Paginator
from django.shortcuts import render_to_response,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail
from django.db import IntegrityError
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt

from wsgiadmin.domains.models import Domain, form_registration_request
from wsgiadmin.domains.tools import *

from django.conf import settings
from wsgiadmin.requests.request import BindRequest

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
@csrf_exempt
def rm(request,did):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	did = int(did)

	d = get_object_or_404(Domain,id=did)
	if d.owner == u:
		logging.info(_(u"Mažu doménu %s")%d.name)
		
		pri_br = BindRequest(u, "master")
		pri_br.remove_zone(d)
		pri_br.reload()
		d.delete()
		pri_br.mod_config()
		sec_br = BindRequest(u, "slave")
		sec_br.mod_config()
		sec_br.reload()
		
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

			instance = Domain()
			instance.name = name
			instance.owner = u
			instance.save()

			pri_br = BindRequest(u, "master")
			pri_br.mod_zone(instance)
			pri_br.mod_config()
			pri_br.reload()
			sec_br = BindRequest(u, "slave")
			sec_br.mod_config()
			sec_br.reload()
				
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
	
