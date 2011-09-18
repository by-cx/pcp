# -*- coding: utf-8 -*-

import logging
import anyjson

from datetime import date
from django.conf import settings

from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.template.context import RequestContext

from wsgiadmin.clients.models import *
from wsgiadmin.apacheconf.models import *
from wsgiadmin.apacheconf.forms import form_static, FormWsgi
from wsgiadmin.requests.request import ApacheRequest, NginxRequest, UWSGIRequest
from wsgiadmin.apacheconf.tools import get_user_wsgis, get_user_venvs, user_directories

info = logging.info

__all__ = ['refresh_venv', 'refresh_wsgi', 'add_static', 'refresh_userdirs', 'update_static']


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

    domains = form.data["domains"].split(" ") # domény u aktuální stránky
    used_domains = [] # Všechny domény použité u aplikací
    my_domains = [x.name for x in u.domain_set.all()]
    error_domains = []

    for site in u.usersite_set.filter(removed=False):
        if site == this_site: continue
        used_domains += site.domains.split(" ")

    # Permission test
    for domain in domains:
        error = domain not in my_domains

        if error and "%s - %s" % (domain, (u"chybí oprávnění k použití")) not in error_domains:
            error_domains.append("%s - %s" % (domain, (u"chybí oprávnění k použití")))

    # Used test
    for domain in domains:
        if domain in used_domains and "%s - %s" % (domain, _(u"už je použitá")) not in error_domains:
            error_domains.append("%s - %s" % (domain, _(u"už je použitá")))

    return error_domains


@login_required
def add_static(request, php="0"):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    title = _(u"Přidání statického webu") if php == "0" else _(u"Přidání webu s podporou PHP")
    siteErrors = []
    choices = [(d, d) for d in user_directories(u, True)]

    if request.method == 'POST':
        form = form_static(request.POST)
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

            if settings.PCP_SETTINGS['mode'] == 'nginx':
                nr = NginxRequest(u, u.parms.web_machine)
                nr.mod_vhosts()
                nr.reload()

            # calculate!
            u.parms.pay_for_sites(use_cache=False)
            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = form_static()
        form.fields["documentRoot"].choices = [("", _(u"Nevybráno"))] + choices

    dynamic_refreshs = (
        (reverse("refresh_userdirs"), 'id_documentRoot'),
    )

    return render_to_response('add_site.html',
            {
            "dynamic_refreshs": dynamic_refreshs,
            "siteErrors": siteErrors,
            "form": form,
            "title": title,
            "submit": _(u"Přidat web"),
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

    s = get_object_or_404(Site, id=sid)
    choices = [(d, d) for d in user_directories(u)]

    if request.method == 'POST':
        form = form_static(request.POST)
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

            if settings.PCP_SETTINGS['mode'] == "nginx":
                nr = NginxRequest(u, u.parms.web_machine)
                nr.mod_vhosts()
                nr.reload()
            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = form_static(initial={"domains": s.domains, "documentRoot": s.documentRoot})
        form.fields["documentRoot"].choices = [("", _(u"Nevybráno"))] + choices


    dynamic_refreshs = (
        (reverse("refresh_userdirs"), 'id_documentRoot'),
    )

    return render_to_response('add_site.html',
            {
            "dynamic_refreshs": dynamic_refreshs,
            "siteErrors": siteErrors,
            "form": form,
            "title": _(u"Úprava statického webu"),
            "submit": _(u"Upravit web"),
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
        return HttpResponseForbidden("Pristup zakazan")

    ur = UWSGIRequest(u, u.parms.web_machine)
    ur.stop(s)

    s.removed = True
    s.end_date = date.today()
    s.save()

    #Signal
    ar = ApacheRequest(u, u.parms.web_machine)
    ar.mod_vhosts()
    ar.reload()

    if settings.PCP_SETTINGS['mode'] == 'nginx':
        nr = NginxRequest(u, u.parms.web_machine)
        nr.mod_vhosts()
        nr.reload()

    ur.mod_config()
    
    # calculate!
    u.parms.pay_for_sites(use_cache=False)
    return HttpResponse("Stránka vymazána")


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

            if settings.PCP_SETTINGS['mode'] == 'nginx':
                nr = NginxRequest(u, u.parms.web_machine)
                nr.mod_vhosts()
                nr.reload()

            if site.type == "uwsgi":
                ur = UWSGIRequest(u, u.parms.web_machine)
                ur.mod_config()
                ur.restart(site)

            # calculate!
            u.parms.pay_for_sites(use_cache=False)
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
            "action": reverse("wsgiadmin.apacheconf.views.add_wsgi"),
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

                if settings.PCP_SETTINGS['mode'] == 'nginx':
                    nr = NginxRequest(u, u.parms.web_machine)
                    nr.mod_vhosts()
                    nr.reload()
            else:
                ar = ApacheRequest(u, u.parms.web_machine)
                ar.mod_vhosts()
                ar.reload()

                if settings.PCP_SETTINGS['mode'] == 'nginx':
                    nr = NginxRequest(u, u.parms.web_machine)
                    nr.mod_vhosts()
                    nr.reload()

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
    s = get_object_or_404(Site, id=sid)

    #Signal
    if s.wsgi.uwsgi:
        ur = UWSGIRequest(u, u.parms.web_machine)
        ur.mod_config()
        ur.restart(s)
    else:
        ar = ApacheRequest(u, u.parms.web_machine)
        ar.mod_vhosts()
        ar.reload()

        if settings.PCP_SETTINGS['mode'] == 'nginx':
            nr = NginxRequest(u, u.parms.web_machine)
            nr.mod_vhosts()
            nr.reload()

    return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))


@login_required
def restart(request, sid):
    u = request.session.get('switched_user', request.user)

    sid = int(sid)
    s = get_object_or_404(Site, id=sid)

    #Signal
    if s.wsgi.uwsgi:
        ur = UWSGIRequest(u, u.parms.web_machine)
        ur.mod_config()
        ur.restart(s)
    else:
        ar = ApacheRequest(u, u.parms.web_machine)
        ar.mod_vhosts()
        ar.restart()

        if settings.PCP_SETTINGS['mode'] == 'nginx':
            nr = NginxRequest(u, u.parms.web_machine)
            nr.mod_vhosts()
            nr.restart()

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
