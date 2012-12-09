# -*- coding: utf-8 -*-
import json
from os.path import join
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.apps.tools import Script
from wsgiadmin.apps.apps import typed_object
from wsgiadmin.clients.forms import UserForm, ParmsForm

from wsgiadmin.clients.models import *
from wsgiadmin.emails.models import Message
from wsgiadmin.requests.request import SystemRequest
from wsgiadmin.service.forms import PassCheckForm, RostiFormHelper
from django.core.exceptions import ObjectDoesNotExist
from wsgiadmin.stats.tools import add_credit

@login_required
def show(request):
    """
    Users list
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden(_("Permission error"))
    u = request.session.get('switched_user', request.user)

    users = list(User.objects.order_by("username").prefetch_related("parms"))

    if request.GET.get("order_by") == "credits":
        users = sorted(users, key=lambda x: x.parms.credit)
    elif request.GET.get("order_by") == "payments":
        users = sorted(users, key=lambda x: x.parms.pay_total_month)

    return render_to_response('users.html',
            {
            "users": users,
            "u": u,
            "superuser": request.user,
            "menu_active": "users",
            },
        context_instance=RequestContext(request)
    )


@login_required
def switch_to_admin(request):
    """
    Přepnutí uživatele
    """
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    current = request.session.get('switched_user', False)

    if current:
        del request.session['switched_user']

    return show(request)


@login_required
def switch_to_user(request, uid):
    """
    Přepnutí uživatele
    """
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    u = request.session.get('switched_user', request.user)
    request.session['switched_user'] = get_object_or_404(User, id=int(uid))

    messages.add_message(request, messages.INFO, _('User has been changed'))
    return show(request)


def install(request, uid):
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    iuser = get_object_or_404(u, id=uid)
    if not iuser.username or ";" in iuser.username:
        return HttpResponseForbidden("Wrong username")

    # System user
    HOME = join("/home", iuser.username)

    #sr = SystemRequest(u, iuser.parms.web_machine)
    #sr.install(iuser)
    #sr.commit()

    #line = sr.run("cat /etc/passwd |grep ^%s:" % iuser.username, instant=True)[0].strip()
    #user, foo, uid, gid, bar = line.split(":", 4)

    #iuser.parms.home = HOME
    #iuser.parms.uid = uid
    #iuser.parms.gid = gid
    #iuser.parms.save()

    add_credit(iuser, 30, free=True)

    iuser.is_active = True
    iuser.save()

    message = Message.objects.filter(purpose="approved_reg")
    if message:
        message[0].send(iuser.email)

    messages.add_message(request, messages.SUCCESS, _('User has been installed'))
    return HttpResponseRedirect(reverse("wsgiadmin.useradmin.views.ok"))


@login_required
def add(request):
    """
       Přidání uživatele
   """
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    if request.method == 'POST':
        f_user = UserForm(request.POST)
        f_parms = ParmsForm(request.POST)
        if f_user.is_valid() and f_parms.is_valid():
            instance_user = f_user.save(commit=False)
            instance_user.is_superuser = False
            instance_user.is_staff = False
            instance_user.save()

            instance_parms = f_parms.save(commit=False)
            instance_parms.user = instance_user
            instance_parms.home = "/"
            instance_parms.uid = 0
            instance_parms.gid = 0
            instance_parms.save()

            return HttpResponseRedirect(reverse("wsgiadmin.useradmin.views.ok"))
    else:
        f_user = UserForm()
        f_parms = ParmsForm()

    return render_to_response('userform.html',
            {
            "form_user": f_user,
            "form_parms": f_parms,
            "title": _(u"Add user"),
            "submit": _(u"Add user"),
            "action": reverse("wsgiadmin.users.views.add"),
            "u": u,
            "superuser": superuser,
            },
                              context_instance=RequestContext(request)
    )


@login_required
def update(request, uid):
    """
       Úprava uživatele
   """
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    iuser = get_object_or_404(User, id=int(uid))
    iparms = iuser.parms

    if request.method == 'POST':
        f_user = UserForm(request.POST, instance=iuser)
        f_parms = ParmsForm(request.POST, instance=iparms)
        if f_user.is_valid() and f_parms.is_valid():
            f_user.save()
            f_parms.save()

            return HttpResponseRedirect(reverse("wsgiadmin.useradmin.views.ok"))
    else:
        f_user = UserForm(instance=iuser)
        f_parms = ParmsForm(instance=iparms)

    return render_to_response('userform.html',
            {
            "form_user": f_user,
            "form_parms": f_parms,
            "title": _(u"User update"),
            "submit": _(u"Update information"),
            "action": reverse("wsgiadmin.users.views.update", args=[uid]),
            "u": u,
            "superuser": superuser,
            "menu_active": "users",
            },
                              context_instance=RequestContext(request)
    )


@login_required
def rm(request, uid):
    """
       Smazání uživatele
       Adresa zůstává kvůli fakturám
   """
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    user = get_object_or_404(User, id=int(uid))
    script = Script(user.parms.web_machine.name)
    try:
        parms = user.parms
    except Exception, e:
        print 'users/views - handle only this exception type'
        print type(e)
        parms = None

    for app in user.app_set.all():
        app = typed_object(app)
        app.uninstall()
        app.commit()
        app.delete()
    for webapp in user.usersite_set.all():
        webapp.delete()
    for mydb in user.mysqldb_set.all():
        script.add_cmd("mysql -u root", stdin="DROP DATABASE %s;" % mydb.dbname)
        mydb.delete()
    for pgdb in user.pgsql_set.all():
        script.add_cmd("dropdb %s" % pgdb.dbname)
        script.add_cmd("dropuser %s" % pgdb.dbname)
        pgdb.delete()
    for email in Email.objects.filter(domain__owner=user):
        script.add_cmd("rm -r /var/mail/%s/%s" % (email.domain.name, email.login))
        email.delete()

    script.add_cmd("rm -r /var/www/%s" % user.username)
    script.add_cmd("userdel -r %s" % user.username)
    script.add_cmd("dropuser %s" % user.username)
    script.add_cmd("rm -r /home/%s" % user.username)
    script.commit()

    if parms:
        parms.delete()
    user.delete()

    return HttpResponseRedirect(reverse("users_list"))


@login_required
def ssh_passwd(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if request.method == 'POST':
        form = PassCheckForm(request.POST)
        if form.is_valid():
            sr = SystemRequest(u, u.parms.web_machine)
            sr.passwd(form.cleaned_data["password1"])

            messages.add_message(request, messages.SUCCESS, _('Password has been changed'))
            return HttpResponseRedirect(reverse("wsgiadmin.useradmin.views.ok"))
    else:
        form = PassCheckForm()

    return render_to_response('universal.html',
            {
            "form": form,
            "form_helper": RostiFormHelper(),
            "title": _("Change password for SSH/FTP"),
            "u": u,
            "superuser": superuser,
            "menu_active": "settings",
            },
                              context_instance=RequestContext(request)
    )
