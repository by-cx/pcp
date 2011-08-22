# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response,get_object_or_404,get_list_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.template.context import RequestContext
from django.core.mail import send_mail
from django.conf import settings

from wsgiadmin.clients.models import *
from wsgiadmin.invoices.models import invoice
from wsgiadmin.useradmin.forms import formReg, formReg2, form_reg_payment

@login_required
def info(request):
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	invoices = invoice.objects.filter(client_address=u.parms.address)

	return render_to_response('info.html',
					{"u":u,"superuser":superuser,"menu_active": "dashboard", "invoices": invoices}, context_instance=RequestContext(request)
					)

@login_required
def ok(request):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	return render_to_response('ok.html',
				{"u":u,"superuser":superuser,}, context_instance=RequestContext(request)
			)

@login_required
def error(request):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	return render_to_response('error.html',
				{"u":u,"superuser":superuser,}, context_instance=RequestContext(request)
			)

@login_required
def message(request,t,m):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	return render_to_response('message.html',
										{
											"type":t,
											"message":m,
											"u":u,
											"superuser":superuser,
										},
	                                    context_instance=RequestContext(request)
									)


@login_required
def changePasswd(request):
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	if request.method == 'POST':
		form = formPassword(request.POST)
		if form.is_valid():
			u.set_password(form.cleaned_data["password1"])
			u.save()
			return HttpResponseRedirect(reverse("useradmin.views.ok"))
	else:
		form = formPassword()

	return render_to_response('universal.html',
							{
								"form":form,
								"title":_(u"Změna hesla do administrace"),
								"submit":_(u"Změnit heslo"),
								"action":reverse("useradmin.views.changePasswd"),
								"u":u,
								"superuser":superuser,
							    "menu_active": "settings",
							},
	                        context_instance=RequestContext(request)
						)


@login_required
def pg(request):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	return render_to_response('info.html',
			{"u":u}, context_instance=RequestContext(request)
	)

def reg(request):
	if request.method == 'POST':
		form1 = formReg(request.POST)
		form2 = formReg2(request.POST)
		form3 = form_reg_payment(request.POST)
		if form1.is_valid() and form2.is_valid() and form3.is_valid():
			# user
			u = user.objects.create_user(form2.cleaned_data["username"],form1.cleaned_data["email"],form2.cleaned_data["password1"])
			u.is_active = False
			u.save()
			# adresa
			a = address()
			a.company				= form1.cleaned_data["company"]
			a.residency_name		= form1.cleaned_data["name"]
			a.residency_street		= form1.cleaned_data["street"]
			a.residency_city		= form1.cleaned_data["city"]
			a.residency_city_num	= form1.cleaned_data["city_num"]
			a.residency_ic			= form1.cleaned_data["ic"]
			a.residency_dic			= form1.cleaned_data["dic"]
			a.residency_email		= form1.cleaned_data["email"]
			a.residency_phone		= form1.cleaned_data["phone"]
			a.save()
			# machine
			m_web = get_object_or_404(machine,name=settings.DEFAULT_WEB_MACHINE)
			m_mail = get_object_or_404(machine,name=settings.DEFAULT_MAIL_MACHINE)
			m_mysql = get_object_or_404(machine,name=settings.DEFAULT_MYSQL_MACHINE)
			m_pgsql = get_object_or_404(machine,name=settings.DEFAULT_PGSQL_MACHINE)
			# parms
			p = parms()
			p.home		    = "/home/"+form2.cleaned_data["username"]
			p.note		    = ""
			p.uid		    = 0
			p.gid		    = 0
			p.discount	    = 0
			p.address	    = a
			p.web_machine	= m_web
			p.mail_machine	= m_mail
			p.mysql_machine	= m_mysql
			p.pgsql_machine	= m_pgsql
			p.user		    = u
			p.save()

			if form3.cleaned_data["pay_method"] == "fee":
				p.fee = settings.PAYMENT_FEE[p.currency]
				p.save()

			message = _(u"Byl registrován nový uživatel.")
			send_mail(_('Nová registrace ')+form1.cleaned_data["name"]+' '+form1.cleaned_data["company"],message,'info@rosti.cz',['cx@initd.cz'],fail_silently=False)

			return HttpResponseRedirect(reverse("useradmin.views.regok"))
	else:
		form1 = formReg()
		form2 = formReg2()
		form3 = form_reg_payment()

	return render_to_response('login_reg.html',
							{
								"form1":form1,
								"form2":form2,
							    "form3":form3,
								"title":_(u"Registrace"),
								"submit":_(u"Registrovat"),
								"action":reverse("useradmin.views.reg")
							},
							context_instance=RequestContext(request)
						)
	
def regok(request):
	return render_to_response('regok.html', context_instance=RequestContext(request))
