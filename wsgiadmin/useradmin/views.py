from random import randint
from time import time
from constance import config
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from os.path import join
from hashlib import md5

from django.contrib import messages
from django.db.models.query_utils import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _, ugettext
from django.template.context import RequestContext
from django.core.mail import send_mail
from django.views.generic.edit import FormView

from wsgiadmin.apacheconf.models import UserSite
from wsgiadmin.clients.models import *
from wsgiadmin.emails.models import Message
from wsgiadmin.requests.request import SSHHandler
from wsgiadmin.service.forms import PassCheckForm, RostiFormHelper
from wsgiadmin.useradmin.forms import formReg, formReg2, SendPwdForm, RegistrationForm
from wsgiadmin.clients.models import Parms


@login_required
def app_copy(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    app = UserSite.objects.get(id=int(request.POST.get("app")))
    new_location = request.POST.get("new_location")

    sh = SSHHandler(request.user, app.owner.parms.web_machine)
    cmd = "cp -a %s %s" % (app.document_root, new_location)
    sh.run(cmd=cmd, instant=True)

    messages.add_message(request, messages.SUCCESS, _('Site has been copied'))

    return HttpResponseRedirect(reverse("master"))


@login_required
def master(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    balance_day = 0
    sites = UserSite.objects.all()
    for site in sites:
        balance_day += site.pay
    balance_month = balance_day * 30

    apps = UserSite.objects.filter(Q(type="static")|Q(type="php"))
    apps = sorted(apps, key=lambda x: x.main_domain.name)

    return render_to_response('master.html', {
        "u": u,
        "superuser": superuser,
        "menu_active": "dashboard",
        "balance_day": balance_day,
        "balance_month": balance_month,
        "apps": apps,
        },
        context_instance=RequestContext(request)
    )


@login_required
def info(request):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    return render_to_response('info.html',
            {
                "u": user,
                "superuser": superuser,
                "menu_active": "dashboard",
                "config": config,
                "not_payed": user.credit_set.filter(date_payed=None),
            },
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

class PasswordView(FormView):
    template_name = 'passwd_form.html'

    def __init__(self, *args, **kwargs):
        super(PasswordView, self).__init__(*args, **kwargs)
        self.success_url = reverse('login')

    def get_form_class(self):
        return SendPwdForm

    def get_context_data(self, **kwargs):
        data = super(PasswordView, self).get_context_data(**kwargs)
        data['form_helper'] = RostiFormHelper()
        data['menu_active'] = "reset_passwd"
        return data

    def form_valid(self, form):
        user = form.user_object

        pwd = md5( str(time()*randint(1, 300)) ).hexdigest()[:7]
        message = ugettext("Your password has been reseted: %s" % pwd)
        user.set_password(pwd)

        try:
            send_mail(_('Password reset'), message, settings.EMAIL_FROM, [user.email], fail_silently=False)
        except:
            pass
        else:
            #save changed password only on notification success
            user.save()

        messages.add_message(self.request, messages.SUCCESS, _("Password has been reseted and sent to your email"))
        return super(PasswordView, self).form_valid(form)


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
            "form_helper": RostiFormHelper(),
            "title": _("Change password for this administration"),
            "u": u,
            "superuser": superuser,
            "menu_active": "settings",
            },
        context_instance=RequestContext(request)
    )

def reg(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # machine
            m_web = get_object_or_404(Machine, name=config.default_web_machine)
            m_mail = get_object_or_404(Machine, name=config.default_mail_machine)
            m_mysql = get_object_or_404(Machine, name=config.default_mysql_machine)
            m_pgsql = get_object_or_404(Machine, name=config.default_pgsql_machine)

            # user
            u = user.objects.create_user(form.cleaned_data["username"],
                                         form.cleaned_data["email"],
                                         form.cleaned_data["password1"])
            u.is_active = False
            u.save()

            # parms
            p = Parms()
            p.home = "/dev/null"
            p.note = ""
            p.uid = 0
            p.gid = 0
            p.discount = 0
            p.web_machine = m_web
            p.mail_machine = m_mail
            p.mysql_machine = m_mysql
            p.pgsql_machine = m_pgsql
            p.user = u
            p.save()

            message = Message.objects.filter(purpose="reg")
            if message:
                message[0].send(form.cleaned_data["email"])

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
        form = RegistrationForm()

    form_helper = FormHelper()
    form_helper.form_tag = False

    return render_to_response('reg.html',
        {
            "form": form,
            "form_helper": form_helper,
            "title": _("Registration"),
            "action": reverse("wsgiadmin.useradmin.views.reg"),
            "config": config,
            "menu_active": "registration",
        },
        context_instance=RequestContext(request)
    )


def regok(request):
    return render_to_response('regok.html', context_instance=RequestContext(request))
