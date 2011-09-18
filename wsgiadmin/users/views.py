# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.clients.models import *
from wsgiadmin.requests.request import SystemRequest

@login_required
def show(request, p=1):
    """
    Vylistování seznamu databází
    """
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponse(u"Chyba oprávnění")

    p = int(p)

    paginator = Paginator(list(user.objects.order_by("username")), 75)

    if not paginator.count:
        page = None
    else:
        page = paginator.page(p)

    ssh_users = []
    sr = SystemRequest(u, u.parms.web_machine)
    data = sr.instant_run("cat /etc/passwd")[0]

    for line in [x.strip().split(":") for x in data.split("\n") if x]:
        ssh_users.append(line[0])

    return render_to_response('users.html',
            {
            "users": page,
            "ssh_users": ssh_users,
            "paginator": paginator,
            "num_page": p,
            "u": u,
            "superuser": superuser,
            },
                              context_instance=RequestContext(request)
    )


@login_required
def switch_to_admin(request, p):
    """
       Přepnutí uživatele
   """
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    current = request.session.get('switched_user', False)

    if current:
        del request.session['switched_user']

    return show(request, p)


@login_required
def switch_to_user(request, uid, p):
    """
       Přepnutí uživatele
   """
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    iuser = get_object_or_404(user, id=int(uid))
    request.session['switched_user'] = iuser

    return show(request, p)


def install(request, uid):
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    iuser = get_object_or_404(user, id=uid)

    if iuser.username and not ";" in iuser.username:
        # System user
        HOME = "/home/%s" % iuser.username

        sr = SystemRequest(u, iuser.parms.web_machine)
        sr.install(iuser)
        sr.commit()

        data = sr.instant_run("cat /etc/passwd")[0]

        for line in [x.strip() for x in data.split("\n")]:
            if iuser.username in line:
                line = line.split(":")
                uid = line[2]
                gid = line[3]
                break

        iuser.parms.home = HOME
        iuser.parms.uid = uid
        iuser.parms.gid = gid
        iuser.is_active = True
        iuser.parms.save()
        iuser.save()

        return HttpResponseRedirect(reverse("wsgiadmin.useradmin.views.ok"))


@login_required
def add(request):
    """
       Přidání uživatele
   """
    superuser = request.user
    u = request.session.get('switched_user', request.user)
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    if request.method == 'POST':
        f_user = form_user(request.POST)
        f_parms = form_parms(request.POST)
        f_address = form_address(request.POST)
        if f_user.is_valid() and f_parms.is_valid() and f_address.is_valid():
            instance_user = f_user.save(commit=False)
            instance_user.is_superuser = False
            instance_user.is_staff = False
            instance_user.save()
            instance_address = f_address.save()

            instance_parms = f_parms.save(commit=False)
            instance_parms.user = instance_user
            instance_parms.home = "/"
            instance_parms.uid = 0
            instance_parms.gid = 0
            instance_parms.address = instance_address
            instance_parms.save()

            set_user_on_server(request, instance_user.id)

            return HttpResponseRedirect(reverse("wsgiadmin.useradmin.views.ok"))
    else:
        f_user = form_user()
        f_parms = form_parms()
        f_address = form_address()

    return render_to_response('userform.html',
            {
            "form_user": f_user,
            "form_parms": f_parms,
            "form_address": f_address,
            "title": _(u"Přidání uživatele"),
            "submit": _(u"Přidat uživatele"),
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
        return HttpResponse("Chyba oprávnění")

    iuser = get_object_or_404(user, id=int(uid))
    iparms = iuser.parms
    iaddress = iparms.address

    if request.method == 'POST':
        f_user = form_user(request.POST, instance=iuser)
        f_parms = form_parms(request.POST, instance=iparms)
        f_address = form_address(request.POST, instance=iaddress)
        if f_user.is_valid() and f_parms.is_valid() and f_address.is_valid():
            instance_user = f_user.save()
            instance_address = f_address.save()
            instance_parms = f_parms.save()

            return HttpResponseRedirect(reverse("wsgiadmin.useradmin.views.ok"))
    else:
        f_user = form_user(instance=iuser)
        f_parms = form_parms(instance=iparms)
        f_address = form_address(instance=iaddress)

    return render_to_response('userform.html',
            {
            "form_user": f_user,
            "form_parms": f_parms,
            "form_address": f_address,
            "title": _(u"Upravení uživatele"),
            "submit": _(u"Upravit uživatele"),
            "action": reverse("wsgiadmin.users.views.update", args=[uid]),
            "u": u,
            "superuser": superuser,
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
        return HttpResponse("Chyba oprávnění")

    iuser = get_object_or_404(user, id=int(uid))
    try:
        iparms = iuser.parms
    except:
        iparms = None

    if iparms: iparms.delete()
    if not ";" in iuser.username:
        sr = SystemRequest(u, iuser.parms.web_machine)
        sr.run("dropuser %s" % iuser.username)
        sr.run("userdel %s" % iuser.username)
        sr.run("groupdel %s" % iuser.username)
    iuser.delete()

    return HttpResponse("Smazáno")


@login_required
def ssh_passwd(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if request.method == 'POST':
        form = formPassword(request.POST)
        if form.is_valid():
            sr = SystemRequest(u, u.parms.web_machine)
            sr.passwd(form.cleaned_data["password1"])

            return HttpResponseRedirect(reverse("wsgiadmin.useradmin.views.ok"))
    else:
        form = formPassword()

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Změna hesla k SSH/SFTP/FTP"),
            "submit": _(u"Změnit heslo"),
            "action": reverse("wsgiadmin.users.views.ssh_passwd"),
            "u": u,
            "superuser": superuser,
            "menu_active": "settings",
            },
                              context_instance=RequestContext(request)
    )
