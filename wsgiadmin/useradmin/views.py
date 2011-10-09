from constance import config
from os.path import join

from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.template.context import RequestContext
from django.core.mail import send_mail

from wsgiadmin.apacheconf.models import UserSite
from wsgiadmin.clients.models import *
from wsgiadmin.invoices.models import invoice
from wsgiadmin.service.forms import PassCheckForm
from wsgiadmin.useradmin.forms import formReg, formReg2, PaymentRegForm
from wsgiadmin.clients.models import Parms

@login_required
def master(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    balance_day = 0
    sites = UserSite.objects.filter(removed=False)
    for site in sites:
        balance_day += site.pay
    balance_month = balance_day * 30

    return render_to_response('master.html', {
        "u": u,
        "superuser": superuser,
        "menu_active": "dashboard",
        "balance_day": balance_day,
        "balance_month": balance_month,
        },
        context_instance=RequestContext(request)
    )

@login_required
def info(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    invoices = invoice.objects.filter(client_address=u.parms.address)

    return render_to_response('info.html',
            {"u": u,
             "superuser": superuser,
             "menu_active": "dashboard",
             "invoices": invoices},
        context_instance=RequestContext(request)
    )


@login_required
def requests(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    requests = u.request_set.order_by("add_date").reverse()

    return render_to_response('requests.html', {
            "u": u,
            "superuser": superuser,
            "menu_active": "dashboard",
            "requests": requests[:20],
        }, context_instance=RequestContext(request)
    )


@login_required
def ok(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    return render_to_response('ok.html',
            {"u": u, "superuser": superuser, },
                              context_instance=RequestContext(request)
    )

@login_required
def change_passwd(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if request.method == 'POST':
        form = PassCheckForm(request.POST)
        if form.is_valid():
            u.set_password(form.cleaned_data["password1"])
            u.save()

            messages.add_message(request, messages.SUCCESS, _('Password has been changed'))
            return HttpResponseRedirect(reverse("wsgiadmin.useradmin.views.change_passwd"))
    else:
        form = PassCheckForm()

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Change password for this administration"),
            "submit": _(u"Change password"),
            "action": reverse("wsgiadmin.useradmin.views.change_passwd"),
            "u": u,
            "superuser": superuser,
            "menu_active": "settings",
            },
                              context_instance=RequestContext(request)
    )

def reg(request):
    if request.method == 'POST':
        form1 = formReg(request.POST)
        form2 = formReg2(request.POST)
        form3 = PaymentRegForm(request.POST)
        if form1.is_valid() and form2.is_valid() and form3.is_valid():
            # user
            u = user.objects.create_user(form2.cleaned_data["username"],
                                         form1.cleaned_data["email"],
                                         form2.cleaned_data["password1"])
            u.is_active = False
            u.save()
            # adresa
            a = Address()
            a.company = form1.cleaned_data["company"]
            a.residency_name = form1.cleaned_data["name"]
            a.residency_street = form1.cleaned_data["street"]
            a.residency_city = form1.cleaned_data["city"]
            a.residency_city_num = form1.cleaned_data["city_num"]
            a.residency_ic = form1.cleaned_data["ic"]
            a.residency_dic = form1.cleaned_data["dic"]
            a.residency_email = form1.cleaned_data["email"]
            a.residency_phone = form1.cleaned_data["phone"]
            a.save()
            # machine
            m_web = get_object_or_404(Machine, name=config.default_web_machine)
            m_mail = get_object_or_404(Machine, name=config.default_mail_machine)
            m_mysql = get_object_or_404(Machine, name=config.default_mysql_machine)
            m_pgsql = get_object_or_404(Machine, name=config.default_pgsql_machine)
            # parms
            p = Parms()
            p.home = join("/home", form2.cleaned_data["username"])
            p.note = ""
            p.uid = 0
            p.gid = 0
            p.discount = 0
            p.address = a
            p.web_machine = m_web
            p.mail_machine = m_mail
            p.mysql_machine = m_mysql
            p.pgsql_machine = m_pgsql
            p.user = u
            p.save()

            if form3.cleaned_data["pay_method"] == "fee":
                p.fee = settings.PAYMENT_FEE[p.currency]
                p.save()

            message = _("New user has been registered.")
            send_mail(_('New registration'),
                      message,
                      settings.EMAIL_FROM,
                [address for (name, address) in settings.ADMINS],
                      fail_silently=True)
            #fail_silently - nechci 500 kvuli neodeslanemu mailu

            return HttpResponseRedirect(
                reverse("wsgiadmin.useradmin.views.regok"))
    else:
        form1 = formReg()
        form2 = formReg2()
        form3 = PaymentRegForm()

    return render_to_response('reg.html',
            {
            "form1": form1,
            "form2": form2,
            "form3": form3,
            "title": _("Registration"),
            "submit": _("Register"),
            "action": reverse("wsgiadmin.useradmin.views.reg")
        },
        context_instance=RequestContext(request)
    )


def regok(request):
    return render_to_response('regok.html', context_instance=RequestContext(request))
