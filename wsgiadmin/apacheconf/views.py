import logging

from constance import config
from datetime import date

from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _, ugettext
from django.template.context import RequestContext

from wsgiadmin.apacheconf.forms import FormStatic, FormWsgi
from wsgiadmin.apacheconf.models import UserSite, SiteDomain
from wsgiadmin.domains.models import Domain
from wsgiadmin.requests.request import UWSGIRequest
from wsgiadmin.apacheconf.tools import get_user_wsgis, get_user_venvs, user_directories, restart_master
from wsgiadmin.service.forms import RostiFormHelper
from wsgiadmin.service.views import JsonResponse, RostiListView

info = logging.info

class AppsListView(RostiListView):

    menu_active = 'webapps'
    template_name = 'apache.html'
    delete_url_reverse = 'remove_site'

    def get_queryset(self):
        return self.user.usersite_set.filter(removed=False).order_by("pub_date")

'''
@login_required
def domain_check(request, form, this_site=None):
    u = request.session.get('switched_user', request.user)
    if not form.is_valid():

    form_domains = form.data["domains"].split() # domains typed in form
    # whatever.count.of.dots.vanyli.net -> vanyli.net
    my_domains = ['.'.join(x.name.split('.')[-2:]) for x in u.domain_set.all()]

    used_domains = []
    for tmp_domains in [one.domains.split() for one in UserSite.objects.filter(owner=u, removed=False) if one != this_site]:
        used_domains += tmp_domains

    error_domains = []
    for domain in form_domains:
        # Permission test
        sld_tld = '.'.join(domain.split('.')[-2:])
        error = sld_tld not in my_domains
        if error and "%s - %s" % (domain, ugettext("Missing permission")) not in error_domains:
            error_domains.append("%s - %s" % (domain, ugettext("Missing permission")))
            continue

        # Used test
        if domain in used_domains and "%s - %s" % (domain, ugettext("Already used")) not in error_domains:
            error_domains.append("%s - %s" % (domain, ugettext("Already used")))

    return error_domains
'''


def get_domains(site, user):
    #TODO - filter main domains as well
    if site:
        exclude_domains = SiteDomain.objects.exclude(user_site=site).values_list('id', flat=True)
    else:
        exclude_domains = SiteDomain.objects.all().values_list('id', flat=True)

    return Domain.objects.filter(owner=user).exclude(id__in=exclude_domains)

@login_required
def app_static(request, app_type="static", app_id=0):
    if app_type not in ("static", "php"):
        return HttpResponseForbidden(ugettext("Invalid type of application"))

    u = request.session.get('switched_user', request.user)
    superuser = request.user

    try:
        site = UserSite.objects.get(id=app_id, owner=u)
    except UserSite.DoesNotExist:
        site = None

    domains = get_domains(site, u)
    domains = u.domain_set.all()
    FormStatic.base_fields['main_domain'].queryset = domains
    FormStatic.base_fields['misc_domains'].queryset = domains
    if request.method == 'POST':
        form = FormStatic(request.POST, user=u, instance=site)

        if form.is_valid():
            isite = form.save(commit=False)
            isite.type = app_type
            isite.owner = u
            isite.save()

            for one in form.cleaned_data['misc_domains']:
                SiteDomain.objects.create(domain=one, user_site=isite)

            # Requests
            restart_master(config.mode, u)

            # calculate!
            u.parms.pay_for_sites(use_cache=False)

            messages.add_message(request, messages.SUCCESS, _('Site has been %s') % (_('changed') if site else _('added')))
            messages.add_message(request, messages.INFO, _('Changes will be performed in few minutes'))
            return HttpResponseRedirect(reverse("app_list"))
    else:
        form = FormStatic(user=u, instance=site)

    form.helper.form_action = reverse("app_static", kwargs={'app_type': app_type, 'app_id': app_id})

    return render_to_response('add_site.html',
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
def app_wsgi(request, app_id=0):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    try:
        site = UserSite.objects.get(id=app_id, owner=u)
    except UserSite.DoesNotExist:
        site = None

    domains = get_domains(site, u)
    FormWsgi.base_fields['main_domain'].queryset = domains
    FormWsgi.base_fields['misc_domains'].queryset = domains
    if request.method == 'POST':
        form = FormWsgi(request.POST, user=u, instance=site)

        if form.is_valid():
            site = form.save(commit=False)
            site.owner = u
            site.type = 'uwsgi'
            site.save()

            for one in form.cleaned_data['misc_domains']:
                SiteDomain.objects.create(domain=one, user_site=site)


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

    form.helper.form_action = reverse("app_wsgi", args=[app_id])

    return render_to_response('add_site.html',
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

    user_dirs = user_directories(request.session.get('switched_user', request.user), use_cache=False)
    return JsonResponse('OK', user_dirs)
