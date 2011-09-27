import logging

from constance import config
from datetime import date
from django.contrib import messages

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _, ugettext
from django.template.context import RequestContext

from wsgiadmin.apacheconf.models import *
from wsgiadmin.apacheconf.forms import FormStatic, FormWsgi
from wsgiadmin.requests.request import UWSGIRequest
from wsgiadmin.apacheconf.tools import get_user_wsgis, get_user_venvs, user_directories, restart_master
from wsgiadmin.service.views import JsonResponse, RostiListView

info = logging.info

class AppsListView(RostiListView):

    menu_active = 'webapps'
    template_name = 'apache.html'

    def get_queryset(self):
        return self.user.usersite_set.filter(removed=False).order_by("pub_date")


@login_required
def domain_check(request, form, this_site=None):
    u = request.session.get('switched_user', request.user)

    form_domains = form.data["domains"].split() # domains typed in form
    my_domains = [str(x.name) for x in u.domain_set.all()]

    used_domains = []
    for tmp_domains in [one.domains.split() for one in UserSite.objects.filter(owner=u, removed=False) if one != this_site]:
        used_domains += tmp_domains

    error_domains = []
    for domain in form_domains:
        # Permission test
        error = domain not in my_domains
        if error and "%s - %s" % (domain, ugettext("Missing permission")) not in error_domains:
            error_domains.append("%s - %s" % (domain, ugettext("Missing permission")))
            continue

        # Used test
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
            restart_master(config.mode, u)

            # calculate!
            u.parms.pay_for_sites(use_cache=False)

            messages.add_message(request, messages.SUCCESS, _('Site has been added'))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("app_list"))
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
            restart_master(config.mode, u)

            messages.add_message(request, messages.SUCCESS, _('Site has been updated'))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("app_list"))
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
            "title": _("Static web modification"),
            "submit": _("Save changes"),
            "action": reverse("update_static", args=[s.id]),
            "u": u,
            "superuser": superuser,
            "menu_active": "webapps",
            },
        context_instance=RequestContext(request)
    )

@login_required
def remove_site(request):
    u = request.session.get('switched_user', request.user)

    try:
        object_id = request.POST['object_id']
        s = get_object_or_404(UserSite, id=object_id)
        if s.owner != u:
            raise Exception("Forbidden operation")

        s.removed = True
        s.end_date = date.today()
        s.save()

        #Signal
        restart_master(config.mode, u)

        ur = UWSGIRequest(u, u.parms.web_machine)
        ur.stop(s)
        ur.mod_config()

        # calculate!
        u.parms.pay_for_sites(use_cache=False)
        return JsonResponse("OK", {1: ugettext("Site was successfuly removed")})
    except Exception, e:
        return JsonResponse("KO", {1: ugettext("Error deleting site")})


@login_required
def app_wsgi(request, sid=None):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    site_errors = []

    try:
        site = UserSite.objects.get(id=sid, owner=u)
    except UserSite.DoesNotExist:
        site = None

    if request.method == 'POST':
        form = FormWsgi(request.POST, user=u, instance=site)

        site_errors = domain_check(request, form, site)
        if not site_errors and form.is_valid():
            site = form.save(commit=False)
            site.owner = u
            site.type = 'uwsgi'
            site.save()

            if site.type == "uwsgi":
                ur = UWSGIRequest(u, u.parms.web_machine)
                ur.mod_config()
                ur.restart(site)

            #Signal
            restart_master(config.mode, u)

            # calculate!
            u.parms.pay_for_sites(use_cache=False)

            messages.add_message(request, messages.SUCCESS, _('App has been %s' % 'changed' if site else 'added'))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("app_list"))
    else:
        form = FormWsgi(user=u, instance=site)


    dynamic_refreshs = (
        (reverse("refresh_wsgi"), 'id_script'),
        (reverse("refresh_venv"), 'id_virtualenv'),
    )

    return render_to_response('add_site.html',
            {
            "dynamic_refreshs": dynamic_refreshs,
            "siteErrors": site_errors,
            "form": form,
            "title": _("%s WSGI application" % 'Modify' if site else 'Add'),
            "submit": _("Save changes"),
            "action": reverse("app_wsgi", args=[site.id] if site else None),
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
        restart_master(config.mode, u)

    messages.add_message(request, messages.SUCCESS, _('Request for reloading has been sent'))
    messages.add_message(request, messages.INFO, _('It will be performed in few minutes'))
    return HttpResponseRedirect(reverse("app_list"))


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
        restart_master(config.mode, u)

    messages.add_message(request, messages.SUCCESS, _('Request for restarting has been sent'))
    messages.add_message(request, messages.INFO, _('It will be performed in few minutes'))
    return HttpResponseRedirect(reverse("app_list"))


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
