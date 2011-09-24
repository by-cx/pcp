# -*- coding: utf-8 -*-

import logging
import anyjson

from constance import config
from datetime import date
from django.contrib import messages

from django.core.paginator import Paginator
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _, ugettext
from django.template.context import RequestContext

from wsgiadmin.apacheconf.models import *
from wsgiadmin.apacheconf.forms import FormStatic, FormWsgi
from wsgiadmin.requests.request import ApacheRequest, NginxRequest, UWSGIRequest
from wsgiadmin.apacheconf.tools import get_user_wsgis, get_user_venvs, user_directories

info = logging.info

__all__ = ['refresh_venv', 'refresh_wsgi', 'add_static', 'refresh_userdirs', 'update_static', 'add_wsgi']


class JsonResponse(HttpResponse):

    def __init__(self, result, messages):
        content = anyjson.serialize(dict(result=result, messages=messages))
        super(JsonResponse, self).__init__(content, content_type='application/jsonrequest')


@login_required
def apache(request, p=1):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    p = int(p)

    paginator = Paginator(list(u.usersite_set.filter(removed=False).order_by("pub_date")), 25)

    if not paginator.count:
        page = None
    else:
        page = paginator.page(p)

    return render_to_response("apache.html",
            {
            "sites": page,
            "paginator": paginator,
            "num_page": p,
            "u": u,
            "superuser": superuser,
            "menu_active": "webapps",
            }, context_instance=RequestContext(request))


@login_required
def domain_check(request, form, this_site=None):
    u = request.session.get('switched_user', request.user)

    domains = form.data["domains"].split() # domény u aktuální stránky
    my_domains = [x.name for x in u.domain_set.all()]

    # Všechny domény použité u aplikací
    used_domains = []
    for tmp_domains in [one.domains.split() for one in UserSite.objects.filter(owner=u, removed=False)]:
        used_domains += tmp_domains

    # Permission test
    error_domains = []
    for domain in domains:
        error = domain not in my_domains
        if error and "%s - %s" % (domain, ugettext("Missing permission")) not in error_domains:
            error_domains.append("%s - %s" % (domain, ugettext("Missing permission")))

    # Used test
    for domain in domains:
        if domain in used_domains and "%s - %s" % (domain, ugettext("Already used")) not in error_domains:
            error_domains.append("%s - %s" % (domain, ugettext("Already used")))

    return error_domains


@login_required
def add_static(request, php="0"):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    title = _("Static website") if php == "0" else _("PHP website")
    siteErrors = []
    choices = [(d, d) for d in user_directories(u, True)]

    if request.method == 'POST':
        form = FormStatic(request.POST)
        form.fields["documentRoot"].choices = choices
        siteErrors = domain_check(request, form)
        if not siteErrors and form.is_valid():
            web = UserSite()
            web.domains = form.cleaned_data["domains"]
            web.documentRoot = form.cleaned_data["documentRoot"]
            web.type = "static" if php == "0" else "php" 
            web.owner = u
            web.save()

            # Requests
            ar = ApacheRequest(u, u.parms.web_machine)
            ar.mod_vhosts()
            ar.reload()

            if config.mode == "nginx":
                nr = NginxRequest(u, u.parms.web_machine)
                nr.mod_vhosts()
                nr.reload()

            # calculate!
            u.parms.pay_for_sites(use_cache=False)

            messages.add_message(request, messages.SUCCESS, _('Site has been added'))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = FormStatic()
        form.fields["documentRoot"].choices = [("", _("Not selected"))] + choices

    dynamic_refreshs = (
        (reverse("refresh_userdirs"), 'id_documentRoot'),
    )

    return render_to_response('add_site.html',
            {
            "dynamic_refreshs": dynamic_refreshs,
            "siteErrors": siteErrors,
            "form": form,
            "title": title,
            "submit": _("Add website"),
            "action": reverse("add_static", args=[php]),
            "u": u,
            "superuser": superuser,
            "menu_active": "webapps",
            },
        context_instance=RequestContext(request)
    )


@login_required
def update_static(request, sid):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    siteErrors = []
    sid = int(sid)

    s = get_object_or_404(UserSite, id=sid)
    choices = [(d, d) for d in user_directories(u)]

    if request.method == 'POST':
        form = FormStatic(request.POST)
        form.fields["documentRoot"].choices = choices
        siteErrors = domain_check(request, form, s)
        if not siteErrors and form.is_valid():
            s.domains = form.cleaned_data["domains"]
            s.documentRoot = form.cleaned_data["documentRoot"]
            s.save()

            #Signal
            ar = ApacheRequest(u, u.parms.web_machine)
            ar.mod_vhosts()
            ar.reload()

            if config.mode == "nginx":
                nr = NginxRequest(u, u.parms.web_machine)
                nr.mod_vhosts()
                nr.reload()

            messages.add_message(request, messages.SUCCESS, _('Site has been updated'))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = FormStatic(initial={"domains": s.domains, "documentRoot": s.documentRoot})
        form.fields["documentRoot"].choices = [("", _("Not selected"))] + choices


    dynamic_refreshs = (
        (reverse("refresh_userdirs"), 'id_documentRoot'),
    )

    return render_to_response('add_site.html',
            {
            "dynamic_refreshs": dynamic_refreshs,
            "siteErrors": siteErrors,
            "form": form,
            "title": _(u"Static web modification"),
            "submit": _(u"Save changes"),
            "action": reverse("update_static", args=[s.id]),
            "u": u,
            "superuser": superuser,
            "menu_active": "webapps",
            },
        context_instance=RequestContext(request)
    )

@login_required
def remove_site(request, sid):
    u = request.session.get('switched_user', request.user)
    sid = int(sid)

    s = get_object_or_404(UserSite, id=sid)
    if s.owner != u:
        return HttpResponseForbidden("Access forbidden")

    ur = UWSGIRequest(u, u.parms.web_machine)
    ur.stop(s)

    s.removed = True
    s.end_date = date.today()
    s.save()

    #Signal
    ar = ApacheRequest(u, u.parms.web_machine)
    ar.mod_vhosts()
    ar.reload()

    if config.mode == 'nginx':
        nr = NginxRequest(u, u.parms.web_machine)
        nr.mod_vhosts()
        nr.reload()

    ur.mod_config()
    
    # calculate!
    u.parms.pay_for_sites(use_cache=False)
    return HttpResponse(_("Site removed"))


@login_required
def add_wsgi(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    siteErrors = []

    if request.method == 'POST':
        form = FormWsgi(request.POST, user=u)
        
        siteErrors = domain_check(request, form)
        if not siteErrors and form.is_valid():
            site = form.save(commit=False)
            site.owner = u
            site.type = 'uwsgi'
            site.save()

            #Signal
            ar = ApacheRequest(u, u.parms.web_machine)
            ar.mod_vhosts()
            ar.reload()

            if config.mode == 'nginx':
                nr = NginxRequest(u, u.parms.web_machine)
                nr.mod_vhosts()
                nr.reload()

            if site.type == "uwsgi":
                ur = UWSGIRequest(u, u.parms.web_machine)
                ur.mod_config()
                ur.restart(site)

            # calculate!
            u.parms.pay_for_sites(use_cache=False)

            messages.add_message(request, messages.SUCCESS, _('App has been added'))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = FormWsgi(user=u)

    dynamic_refreshs = (
        (reverse("refresh_wsgi"), 'id_script'),
        (reverse("refresh_venv"), 'id_virtualenv'),
    )

    return render_to_response('add_site.html',
            {
            "dynamic_refreshs": dynamic_refreshs,
            "siteErrors": siteErrors,
            "form": form,
            "title": _(u"Přidání WSGI aplikace"),
            "submit": _(u"Přidat WSGI aplikaci"),
            "action": reverse("add_wsgi"),
            "u": u,
            "superuser": superuser,
            "menu_active": "webapps",
            },
        context_instance=RequestContext(request)
    )


@login_required
def update_wsgi(request, sid):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    siteErrors = []

    sid = int(sid)
    site = get_object_or_404(u.usersite_set, id=sid)

    if request.method == 'POST':
        form = FormWsgi(request.POST, user=u, instance=site)

        siteErrors = domain_check(request, form, site)
        if not siteErrors and form.is_valid():
            site = form.save()

            #Signal
            if site.type == "uwsgi":
                ur = UWSGIRequest(u, u.parms.web_machine)
                ur.mod_config()
                ur.restart(site)

                ar = ApacheRequest(u, u.parms.web_machine)
                ar.mod_vhosts()
                ar.reload()

                if config.mode == 'nginx':
                    nr = NginxRequest(u, u.parms.web_machine)
                    nr.mod_vhosts()
                    nr.reload()
            else:
                ar = ApacheRequest(u, u.parms.web_machine)
                ar.mod_vhosts()
                ar.reload()

                if config.mode == 'nginx':
                    nr = NginxRequest(u, u.parms.web_machine)
                    nr.mod_vhosts()
                    nr.reload()

            messages.add_message(request, messages.SUCCESS, _('App has been updated'))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = FormWsgi(user=u, instance=site)


    dynamic_refreshs = (
        (reverse("refresh_wsgi"), 'id_script'),
        (reverse("refresh_venv"), 'id_virtualenv'),
    )

    return render_to_response('add_site.html',
            {
            "dynamic_refreshs": dynamic_refreshs,
            "siteErrors": siteErrors,
            "form": form,
            "title": _(u"Upravení WSGI aplikace"),
            "submit": _(u"Upravit WSGI aplikaci"),
            "action": reverse("wsgiadmin.apacheconf.views.update_wsgi", args=[site.id]),
            "u": u,
            "superuser": superuser,
            "menu_active": "webapps",
            },
        context_instance=RequestContext(request)
    )


@login_required
def reload(request, sid):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    sid = int(sid)
    s = get_object_or_404(UserSite, id=sid)

    #Signal
    if s.type in ("uwsgi", "modwsgi"):
        ur = UWSGIRequest(u, u.parms.web_machine)
        ur.mod_config()
        ur.restart(s)
    else:
        ar = ApacheRequest(u, u.parms.web_machine)
        ar.mod_vhosts()
        ar.reload()

        if config.mode == 'nginx':
            nr = NginxRequest(u, u.parms.web_machine)
            nr.mod_vhosts()
            nr.reload()

    messages.add_message(request, messages.SUCCESS, _('Request for reloading has been sent'))
    messages.add_message(request, messages.INFO, _('It will be performed in few minutes'))
    return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))


@login_required
def restart(request, sid):
    u = request.session.get('switched_user', request.user)

    sid = int(sid)
    s = get_object_or_404(UserSite, id=sid)

    #Signal
    if s.type in ("uwsgi", "modwsgi"):
        ur = UWSGIRequest(u, u.parms.web_machine)
        ur.mod_config()
        ur.restart(s)
    else:
        ar = ApacheRequest(u, u.parms.web_machine)
        ar.mod_vhosts()
        ar.restart()

        if config.mode == 'nginx':
            nr = NginxRequest(u, u.parms.web_machine)
            nr.mod_vhosts()
            nr.restart()

    messages.add_message(request, messages.SUCCESS, _('Request for restarting has been sent'))
    messages.add_message(request, messages.INFO, _('It will be performed in few minutes'))
    return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))


@login_required
def refresh_wsgi(request):
    if not (request.method == 'POST' and request.is_ajax()):
        return HttpResponseForbidden('non ajax not allowed')

    wsgis = get_user_wsgis(request.session.get('switched_user', request.user), False)
    return JsonResponse('OK', wsgis)

@login_required
def refresh_venv(request):
    if not (request.method == 'POST' and request.is_ajax()):
        return HttpResponseForbidden('non ajax not allowed')

    venvs = get_user_venvs(request.session.get('switched_user', request.user), False)
    return JsonResponse('OK', venvs)


@login_required
def refresh_userdirs(request):
    if not (request.method == 'POST' and request.is_ajax()):
        return HttpResponseForbidden('non ajax not allowed')

    user_dirs = user_directories(request.session.get('switched_user', request.user), False)
    return JsonResponse('OK', user_dirs)
