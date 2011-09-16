# -*- coding: utf-8 -*-

import logging
from os.path import join
from datetime import date
import anyjson

from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.template.context import RequestContext
from django.conf import settings
from django.core.cache import cache

from wsgiadmin.clients.models import *
from wsgiadmin.apacheconf.models import *
from wsgiadmin.apacheconf.forms import form_static, form_wsgi
from wsgiadmin.requests.request import ApacheRequest, NginxRequest, UWSGIRequest, SSHHandler
from wsgiadmin.apacheconf.tools import find_user_wsgis, find_user_venvs

info = logging.info

__all__ = ['refresh_venv', 'refresh_wsgi']


class JsonResponse(HttpResponse):

    def __init__(self, result, messages):
        content = anyjson.serialize(dict(result=result, messages=messages))
        super(JsonResponse, self).__init__(content, content_type='application/jsonrequest')


def user_directories(u):
    sh = SSHHandler(u, u.parms.web_machine)
    dirs = sh.instant_run("/usr/bin/find %s -maxdepth 2 -type d" % u.parms.home)[0].split("\n")

    return [d.strip() for d in dirs if d and not "/." in d]


@login_required
def apache(request, p=1):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    p = int(p)

    paginator = Paginator(list(u.site_set.filter(removed=False)), 25)

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
            })


@login_required
def domain_check(request, form, this_site=None):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    domains = form.data["domains"].split(" ") # domény u aktuální stránky
    print domains
    used_domains = [] # Všechny domény použité u aplikací
    my_domains = [x.name for x in u.domain_set.all()]
    error_domains = []

    for site in u.site_set.filter(removed=False):
        if site == this_site: continue
        used_domains += site.domains.split(" ")

    # Perm test
    for domain in domains:
        error = True
        for my_domain in my_domains:
            if my_domain in domain:
                error = False

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
    siteErrors = []

    choices = [(d, d) for d in user_directories(u)]

    if request.method == 'POST':
        form = form_static(request.POST)
        form.fields["documentRoot"].choices = choices
        siteErrors = domain_check(request, form)
        if not siteErrors and form.is_valid():
            web = Site()
            web.domains = form.cleaned_data["domains"]
            web.documentRoot = form.cleaned_data["documentRoot"]
            web.type = "static" if php == "0" else "php" 
            web.owner = u
            web.save()

            # Requests

            ar = ApacheRequest(u, u.parms.web_machine)
            ar.mod_vhosts()
            ar.reload()

            nr = NginxRequest(u, u.parms.web_machine)
            nr.mod_vhosts()
            nr.reload()

            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = form_static()
        form.fields["documentRoot"].choices = choices

    if php == "0":
        title = _(u"Přidání statického webu")
    else:
        title = _(u"Přidání webu s podporou PHP")

    return render_to_response('universal.html',
            {
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

            nr = NginxRequest(u, u.parms.web_machine)
            nr.mod_vhosts()
            nr.reload()

            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = form_static(initial={"domains": s.domains, "documentRoot": s.documentRoot})
        form.fields["documentRoot"].choices = choices

    return render_to_response('universal.html',
            {
            "siteErrors": siteErrors,
            "form": form,
            "title": _(u"Úprava statického webu"),
            "submit": _(u"Upravit web"),
            "action": reverse("wsgiadmin.apacheconf.views.update_static", args=[s.id]),
            "u": u,
            "superuser": superuser,
            "menu_active": "webapps",
            },
        context_instance=RequestContext(request)
    )


@login_required
def remove_site(request, sid):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    sid = int(sid)

    s = get_object_or_404(Site, id=sid)
    if s.owner == u:
        ur = UWSGIRequest(u, u.parms.web_machine)
        ur.stop(s)

        s.removed = True
        s.end_date = date.today()
        s.save()

        #Signal
        ar = ApacheRequest(u, u.parms.web_machine)
        ar.mod_vhosts()
        ar.reload()

        nr = NginxRequest(u, u.parms.web_machine)
        nr.mod_vhosts()
        nr.reload()

        ur.mod_config()

    return HttpResponse("Stránka vymazána")


@login_required
def add_wsgi(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    siteErrors = []

    wsgis = cache.get('user_caches_%s' % u.pk)
    if not wsgis:
        wsgis = find_user_wsgis(u)
        if wsgis:
            cache.set('user_caches_%s' % u.pk, wsgis, timeout=3600*24*7)
    choices = [("", _(u"Nevybráno"))] + [(x, x) for x in wsgis]


    sh = SSHHandler(u, u.parms.web_machine)
    virtualenvs = cache.get('user_venvs_%s' % u.pk)
    if not virtualenvs:
        virtualenvs = find_user_venvs(u)
        if virtualenvs:
            cache.set('user_venvs_%s' % u.pk, virtualenvs, timeout=2600*24*7)
    virtualenvs_choices = [("", _(u"Nevybráno"))] + [(one, one) for one in virtualenvs]


    if request.method == 'POST':
        form = form_wsgi(request.POST)
        form.fields["script"].choices = choices
        form.fields["virtualenv"].choices = virtualenvs_choices
        siteErrors = domain_check(request, form)
        if not siteErrors and form.is_valid():
            site = Site()
            site.domains = form.cleaned_data["domains"]
            site.owner = u
            site.virtualenv = form.cleaned_data["virtualenv"]
            site.static = form.cleaned_data["static"]
            site.python_path = form.cleaned_data["python_path"]
            site.script = form.cleaned_data["script"]
            site.allow_ips = form.cleaned_data["allow_ips"]
            site.type = "uwsgi"
            site.save()

            #Signal
            ar = ApacheRequest(u, u.parms.web_machine)
            ar.mod_vhosts()
            ar.reload()

            nr = NginxRequest(u, u.parms.web_machine)
            nr.mod_vhosts()
            nr.reload()
            if site.type == "uwsgi":
                ur = UWSGIRequest(u, u.parms.web_machine)
                ur.mod_config()
                ur.restart(site)

            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = form_wsgi()
        form.fields["script"].choices = choices
        form.fields["virtualenv"].choices = virtualenvs_choices

    return render_to_response('add_wsgi.html',
            {
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


    sh = SSHHandler(u, u.parms.web_machine)
    wsgis = cache.get('user_wsgis_%s' % u.pk)
    if not wsgis:
        wsgis = find_user_wsgis(u)
        if wsgis:
            cache.set('user_wsgis_%s' % u.pk, wsgis, timeout=3600*24*7)
    choices = [("", _(u"Nevybráno"))] + [(x, x) for x in wsgis]


    sh = SSHHandler(u, u.parms.web_machine)
    virtualenvs = cache.get('user_venvs_%s' % u.pk)
    if not virtualenvs:
        virtualenvs = find_user_venvs(u)
        if virtualenvs:
            cache.set('user_venvs_%s' % u.pk, virtualenvs, timeout=2600*24*7)
    virtualenvs_choices = [("", _(u"Nevybráno"))] + [(one, one) for one in virtualenvs]

    sid = int(sid)
    site = get_object_or_404(u.site_set, id=sid)

    if request.method == 'POST':
        form = form_wsgi(request.POST)
        form.fields["script"].choices = choices
        form.fields["virtualenv"].choices = virtualenvs_choices
        siteErrors = domain_check(request, form, site)
        if not siteErrors and form.is_valid():
            site.domains = form.cleaned_data["domains"]
            site.virtualenv = form.cleaned_data["virtualenv"]
            site.static = form.cleaned_data["static"]
            site.script = form.cleaned_data["script"]
            site.python_path = form.cleaned_data["python_path"]
            site.allow_ips = form.cleaned_data["allow_ips"]
            site.save()

            #Signal
            if site.type == "uwsgi":
                ur = UWSGIRequest(u, u.parms.web_machine)
                ur.mod_config()
                ur.restart(site)
                ar = ApacheRequest(u, u.parms.web_machine)
                ar.mod_vhosts()
                ar.reload()

                nr = NginxRequest(u, u.parms.web_machine)
                nr.mod_vhosts()
                nr.reload()
            else:
                ar = ApacheRequest(u, u.parms.web_machine)
                ar.mod_vhosts()
                ar.reload()

                nr = NginxRequest(u, u.parms.web_machine)
                nr.mod_vhosts()
                nr.reload()

            return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))
    else:
        form = form_wsgi(
            initial={"domains": site.domains, "script": site.script, "allow_ips": site.allow_ips, "static": site.static,
                     "virtualenv": site.virtualenv, "python_path": site.python_path})
        form.fields["script"].choices = choices
        form.fields["virtualenv"].choices = virtualenvs_choices

    return render_to_response('universal.html',
            {
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

        nr = NginxRequest(u, u.parms.web_machine)
        nr.mod_vhosts()
        nr.reload()

    return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))


@login_required
def restart(request, sid):
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
        ar.restart()

        nr = NginxRequest(u, u.parms.web_machine)
        nr.mod_vhosts()
        nr.restart()

    return HttpResponseRedirect(reverse("wsgiadmin.apacheconf.views.apache"))


@login_required
def refresh_wsgi(request):
    if not (request.method == 'POST' and request.is_ajax()):
        pass#raise Http404('.(')

    wsgis = find_user_wsgis(request.session.get('switched_user', request.user))
    return JsonResponse('OK', wsgis)

@login_required
def refresh_venv(request):
    if not (request.method == 'POST' and request.is_ajax()):
        pass#raise Http404('.(')

    venvs = find_user_venvs(request.session.get('switched_user', request.user))
    return JsonResponse('OK', venvs)
