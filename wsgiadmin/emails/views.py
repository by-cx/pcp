# -*- coding: utf-8 -*-

import crypt
from datetime import date
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _, ugettext

from wsgiadmin.emails.forms import FormEmail, FormEmailPassword, FormRedirect
from wsgiadmin.emails.models import Email, EmailRedirect
from wsgiadmin.requests.request import EMailRequest


@login_required
def boxes(request, p=1):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    p = int(p)

    emails = list(Email.objects.filter(domain__in=u.domain_set.all(), remove=False))
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
def addBox(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    domains = [(x.name, x.name) for x in u.domain_set.filter(mail=True)]

    if request.method == 'POST':
        form = FormEmail(request.POST)
        form.fields["xdomain"].choices = domains

        if form.is_valid():
            form.cleaned_data["xdomain"] = get_object_or_404(u.domain_set, name=
            form.cleaned_data["xdomain"])
            email = form.save(commit=False)
            email.login = form.cleaned_data["login"]
            email.domain = form.cleaned_data["xdomain"]
            email.pub_date = date.today()
            email.password = crypt.crypt(form.cleaned_data["password1"],
                                         form.cleaned_data["login"])
            email.save()

            er = EMailRequest(u, u.parms.mail_machine)
            er.create_mailbox(email)

            messages.add_message(request, messages.INFO, _('Box will be created in few minutes'))
            return HttpResponseRedirect(reverse("wsgiadmin.emails.views.boxes"))
    else:
        form = FormEmail()
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

    mail = Email.objects.filter(domain__in=u.domain_set.all(), id=eid)[0]
    if mail:
        mail.remove = True
        mail.save()

        er = EMailRequest(u, u.parms.mail_machine)
        er.remove_mailbox(mail)

        messages.add_message(request, messages.SUCCESS, _('Box has been deleted'))
        return HttpResponseRedirect(reverse("wsgiadmin.emails.views.boxes"))

    return HttpResponseNotFound("Mailbox not found .(")


@login_required
def changePasswdBox(request, eid):
    eid = int(eid)
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    e = Email.objects.filter(domain__in=u.domain_set.all(), id=eid)[0]

    if request.method == 'POST':
        form = FormEmailPassword(request.POST, instance=e)
        if form.is_valid():
            email = form.save(commit=False)
            email.password = crypt.crypt(form.cleaned_data["password1"], email.login)
            email.save()
            messages.add_message(request, messages.SUCCESS, _('Password has been changed'))
            return HttpResponseRedirect(reverse("wsgiadmin.emails.views.boxes"))
    else:
        form = FormEmailPassword(instance=e)

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Změna hesla e-mailové schránky"),
            "submit": _(u"Změnit heslo"),
            "action": reverse("wsgiadmin.emails.views.changePasswdBox", args=[e.id]),
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

    redirects = EmailRedirect.objects.filter(domain__in=u.domain_set.all())
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

    r = get_object_or_404(EmailRedirect, id=rid)
    if r.domain.owner != u:
        return HttpResponseForbidden(ugettext("Forbidden operation"))

    r.delete()

    messages.add_message(request, messages.SUCCESS, _('Redirect has been removed'))
    return HttpResponseRedirect(reverse("wsgiadmin.emails.views.redirects"))


@login_required
def changeRedirect(request, rid):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    rid = int(rid)

    r = get_object_or_404(redirect, id=rid)
    if r.domain.owner != u:
        return HttpResponseForbidden(ugettext("Forbidden operation"))

    domains = [(x.name, x.name) for x in u.domain_set.filter(mail=True)]
    if request.method == 'POST':
        form = FormRedirect(request.POST, instance=r)
        form.fields["_domain"].choices = domains
        if form.is_valid():
            fredirect = form.save(commit=False)
            fredirect.domain = get_object_or_404(u.domain_set, name=form.cleaned_data["_domain"])
            fredirect.save()
            messages.add_message(request, messages.SUCCESS, _('Redirect has been changed'))
            return HttpResponseRedirect(reverse("wsgiadmin.emails.views.redirects"))
    else:
        form = FormRedirect(instance=r)
        form.fields["_domain"].choices = domains

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _("Modify email alias"),
            "submit": _("Save changes"),
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
        form = FormRedirect(request.POST)
        form.fields["_domain"].choices = domains
        if form.is_valid():
            redirect = form.save(commit=False)
            redirect.alias = form.cleaned_data["alias"]
            redirect.domain = get_object_or_404(u.domain_set, name=form.cleaned_data["_domain"])
            redirect.pub_date = date.today()
            redirect.save()

            messages.add_message(request, messages.SUCCESS, _('Redirect has been added'))
            return HttpResponseRedirect(reverse("wsgiadmin.emails.views.redirects"))
    else:
        form = FormRedirect()
        form.fields["_domain"].choices = domains

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _("Add email redirect"),
            "submit": _("Add redirect"),
            "action": reverse("wsgiadmin.emails.views.addRedirect"),
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
        context_instance=RequestContext(request)
    )
