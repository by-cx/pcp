# -*- coding: utf-8 -*-

import crypt
from django.core.paginator import Paginator
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from wsgiadmin.emails.models import *
from django.core.urlresolvers import reverse
from wsgiadmin.clients.models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from wsgiadmin.requests.request import EMailRequest
from django.template.context import RequestContext

from django.utils.translation import ugettext_lazy as _, ugettext

@login_required
def boxes(request, p=1):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    p = int(p)

    emails = []
    domains = list(u.domain_set.all())
    for idomain in domains:
        for iemail in list(idomain.email_set.filter(remove=False)):
            emails.append(iemail)

    paginator = Paginator(emails, 25)

    if not paginator.count:
        page = None
    else:
        page = paginator.page(p)

    return render_to_response("boxes.html",
            {
            "emails": page,
            "paginator": paginator,
            "num_page": p,
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            }, context_instance=RequestContext(request))


@login_required
def emailInfo(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    return render_to_response("email_info.html",
            {"u": u, }, context_instance=RequestContext(request)
    )


@login_required
def addBox(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    domains = [(x.name, x.name) for x in u.domain_set.filter(mail=True)]

    if request.method == 'POST':
        form = formEmail(request.POST)
        form.fields["xdomain"].choices = domains

        if form.is_valid():
            form.cleaned_data["xdomain"] = get_object_or_404(u.domain_set, name=
            form.cleaned_data["xdomain"])
            email = form.save(commit=False)
            email.login = form.cleaned_data["login"]
            email.domain = form.cleaned_data["xdomain"]
            email.pub_date = datetime.date.today()
            email.password = crypt.crypt(form.cleaned_data["password1"],
                                         form.cleaned_data["login"])
            email.save()

            er = EMailRequest(u, u.parms.mail_machine)
            er.create_mailbox(email)

            return HttpResponseRedirect(reverse("wsgiadmin.emails.views.boxes"))
    else:
        form = formEmail()
        form.fields["xdomain"].choices = domains

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Přidání e-mailové schránky"),
            "submit": _(u"Přidat schránku"),
            "action": reverse("wsgiadmin.emails.views.addBox"),
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
        context_instance=RequestContext(request)
    )


@login_required
def removeBox(request, eid):
    eid = int(eid)
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    for domain in [x.email_set.all() for x in u.domain_set.all()]:
        for email in domain:
            if email.id == eid:
                email.remove = True
                email.save()

                er = EMailRequest(u, u.parms.mail_machine)
                er.remove_mailbox(email)

                return HttpResponse("Schránka vymazána")
    return HttpResponseNotFound("Not found .(")


@login_required
def changePasswdBox(request, eid):
    eid = int(eid)
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    e = None

    for domain in [x.email_set.all() for x in u.domain_set.all()]:
        for email in domain:
            if email.id == eid:
                e = email
                break
        if e:
            break

    if request.method == 'POST':
        form = formEmailPassword(request.POST, instance=e)
        if form.is_valid():
            email = form.save(commit=False)
            email.password = crypt.crypt(form.cleaned_data["password1"], email.login)
            email.save()
            return HttpResponseRedirect(reverse("wsgiadmin.emails.views.boxes"))
    else:
        form = formEmailPassword(instance=e)

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Změna hesla e-mailové schránky"),
            "submit": _(u"Změnit heslo"),
            "action": reverse("wsgiadmin.emails.views.changePasswdBox",
                              args=[e.id]),
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
                              context_instance=RequestContext(request)
    )


@login_required
def redirects(request, p=1):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    p = int(p)

    redirects = []
    domains = list(u.domain_set.all())
    for idomain in domains:
        for iredirect in list(idomain.redirect_set.all()):
            redirects.append(iredirect)

    paginator = Paginator(redirects, 25)

    if not paginator.count:
        page = None
    else:
        page = paginator.page(p)

    return render_to_response("redirects.html",
            {
            "redirects": page,
            "paginator": paginator,
            "num_page": p,
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
                              context_instance=RequestContext(request))


@login_required
def removeRedirect(request, rid):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    rid = int(rid)

    r = get_object_or_404(redirect, id=rid)
    if not r.domain.owner == u:
        return HttpResponseForbidden(ugettext("Forbidden operation"))

    r.delete()

    return HttpResponse("Přesměrování vymazáno")


@login_required
def changeRedirect(request, rid):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    rid = int(rid)

    r = get_object_or_404(redirect, id=rid)
    if not r.domain.owner == u:
        return HttpResponseForbidden(ugettext("Forbidden operation"))

    domains = [(x.name, x.name) for x in u.domain_set.filter(mail=True)]
    if request.method == 'POST':
        form = formRedirect(request.POST, instance=r)
        form.fields["_domain"].choices = domains
        if form.is_valid():
            fredirect = form.save(commit=False)
            fredirect.domain = get_object_or_404(u.domain_set, name=form.cleaned_data["_domain"])
            fredirect.save()
            return HttpResponseRedirect(reverse("wsgiadmin.emails.views.redirects"))
    else:
        form = formRedirect(instance=r)
        form.fields["_domain"].choices = domains

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Upravení přesměrování"),
            "submit": _(u"Upravit přesměrování"),
            "action": reverse("wsgiadmin.emails.views.changeRedirect", args=[rid]),
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
        context_instance=RequestContext(request)
    )


@login_required
def addRedirect(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    
    domains = [(x.name, x.name) for x in u.domain_set.filter(mail=True)]
    if request.method == 'POST':
        form = formRedirect(request.POST)
        form.fields["_domain"].choices = domains
        if form.is_valid():
            redirect = form.save(commit=False)
            redirect.alias = form.cleaned_data["alias"]
            redirect.domain = get_object_or_404(u.domain_set, name=form.cleaned_data["_domain"])
            redirect.pub_date = datetime.date.today()
            redirect.save()
            return HttpResponseRedirect(reverse("wsgiadmin.emails.views.redirects"))
    else:
        form = formRedirect()
        form.fields["_domain"].choices = domains

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Přidání redirectu"),
            "submit": _(u"Přidat redirect"),
            "action": reverse("wsgiadmin.emails.views.addRedirect"),
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
        context_instance=RequestContext(request)
    )
