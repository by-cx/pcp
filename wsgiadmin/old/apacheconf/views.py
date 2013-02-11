import logging

from constance import config

from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _, ugettext
from django.template.context import RequestContext

from wsgiadmin.old.apacheconf.forms import FormStatic, FormWsgi
from wsgiadmin.old.apacheconf.models import UserSite, SiteDomain
from wsgiadmin.old.domains.tools import domains_list, used_domains
from wsgiadmin.old.requests.request import UWSGIRequest
from wsgiadmin.old.apacheconf.tools import get_user_wsgis, get_user_venvs, user_directories, restart_master, remove_app_preparation
from wsgiadmin.service.views import JsonResponse, RostiListView

info = logging.info

class AppsListView(RostiListView):

    menu_active = 'webapps'
    template_name = 'old/apache.html'
    delete_url_reverse = 'remove_site'

    def get_queryset(self):
        return self.user.usersite_set.order_by("pub_date")

@login_required
def app_static(request, app_type="static", app_id=0):
    if app_type not in ("static", "php"):
        return HttpResponseForbidden(ugettext("Invalid type of application"))

    u = request.session.get('switched_user', request.user)
    superuser = request.user

    try:
        site = u.usersite_set.get(id=app_id)
    except UserSite.DoesNotExist:
        site = None

    domains = domains_list(u, used=used_domains(u, site))
    if request.method == 'POST':
        form = FormStatic(request.POST, user=u, instance=site)
        form.fields["main_domain"].choices = [(x.id, x.domain_name) for x in domains]
        form.fields["misc_domains"].choices = [(x.id, x.domain_name) for x in domains]

        if form.is_valid():
            isite = form.save(commit=False)
            isite.type = app_type
            isite.owner = u
            isite.save()

            for sd in SiteDomain.objects.filter(user_site=isite):
                sd.delete()
            for domain in form.cleaned_data['misc_domains']:
                SiteDomain.objects.create(domain=domain, user_site=isite)

            # Requests
            restart_master(config.mode, u)

            # calculate!
            u.parms.pay_for_sites(use_cache=False)

            messages.add_message(request, messages.SUCCESS, _('Site has been %s') % (_('changed') if site else _('added')))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("app_list"))
    else:
        form = FormStatic(user=u, instance=site)
        form.fields["main_domain"].choices = [(x.id, x.domain_name) for x in domains]
        form.fields["misc_domains"].choices = [(x.id, x.domain_name) for x in domains]

    form.helper.form_action = reverse("app_static", kwargs={'app_type': app_type, 'app_id': app_id})

    return render_to_response('old/add_site.html',
            {
            "form": form,
            "title": {'static': _("Static website"), 'php': _("PHP website")}[app_type],
            "u": u,
            "superuser": superuser,
            "menu_active": "webapps",
            },
        context_instance=RequestContext(request)
    )


@login_required
def remove_site(request):
    user = request.session.get('switched_user', request.user)

    try:
        object_id = request.POST['object_id']
        spp = get_object_or_404(user.usersite_set, id=int(object_id))
        if spp.owner != user:
            raise Exception("Forbidden operation")
        remove_app_preparation(spp)
        spp.delete()
        return JsonResponse("OK", {1: ugettext("Site was successfuly removed")})
    except Exception, e:
        return JsonResponse("KO", {1: ugettext("Error deleting site")})


@login_required
def app_wsgi(request, app_id=0):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    try:
        site = u.usersite_set.get(id=app_id)
    except UserSite.DoesNotExist:
        site = None

    domains = domains_list(u, used=used_domains(u, site))
    if request.method == 'POST':
        form = FormWsgi(request.POST, user=u, instance=site)
        form.fields["main_domain"].choices = [(x.id, x.domain_name) for x in domains]
        form.fields["misc_domains"].choices = [(x.id, x.domain_name) for x in domains]

        if form.is_valid():
            site = form.save(commit=False)
            site.owner = u
            site.type = 'uwsgi'
            site.save()

            for sd in SiteDomain.objects.filter(user_site=site):
                sd.delete()
            for domain in form.cleaned_data['misc_domains']:
                SiteDomain.objects.create(domain=domain, user_site=site)

            if site.type == "uwsgi":
                ur = UWSGIRequest(u, u.parms.web_machine)
                ur.mod_config()
                ur.restart(site)

            #Signal
            restart_master(config.mode, u)

            # calculate!
            u.parms.pay_for_sites(use_cache=False)

            messages.add_message(request, messages.SUCCESS, _('App has been %s') % (_('changed') if site else _('added')))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("app_list"))
    else:
        form = FormWsgi(user=u, instance=site)
        form.fields["main_domain"].choices = [(x.id, x.domain_name) for x in domains]
        form.fields["misc_domains"].choices = [(x.id, x.domain_name) for x in domains]

    form.helper.form_action = reverse("app_wsgi", args=[app_id])

    return render_to_response('old/add_site.html',
            {
            "form": form,
            "title": _("%s WSGI application") % _('Modify') if site else _('Add'),
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
    s = get_object_or_404(u.usersite_set, id=sid)

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
    s = get_object_or_404(u.usersite_set, id=sid)

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
    if not request.is_ajax():
        return HttpResponseForbidden('non ajax not allowed')

    wsgis = get_user_wsgis(request.session.get('switched_user', request.user), False)

    return JsonResponse('OK', wsgis)

@login_required
def refresh_venv(request):
    if not request.is_ajax():
        return HttpResponseForbidden('non ajax not allowed')

    venvs = get_user_venvs(request.session.get('switched_user', request.user), False)
    return JsonResponse('OK', venvs)


@login_required
def refresh_userdirs(request):
    if not request.is_ajax():
        return HttpResponseForbidden('non ajax not allowed')

    user_dirs = user_directories(request.session.get('switched_user', request.user), use_cache=False)
    print user_dirs
    return JsonResponse('OK', user_dirs)
