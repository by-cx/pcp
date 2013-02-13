import logging

from constance import config

from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf import settings
from wsgiadmin.old.apacheconf.tools import remove_app_preparation

from wsgiadmin.old.domains.forms import FormDomain
from wsgiadmin.old.domains.models import Domain
from wsgiadmin.old.requests.request import BindRequest
from wsgiadmin.service.forms import RostiFormHelper
from wsgiadmin.service.views import JsonResponse, RostiListView, RostiUpdateView


class DomainsListView(RostiListView):
    menu_active = 'domains'
    template_name = 'domains.html'
    delete_url_reverse = 'domain_remove'

    def get_queryset(self):
        return self.user.domain_set.filter(parent=None).order_by("name")

class DomainUpdateView(RostiUpdateView):
    success_url = "/domains/show/"
    menu_active = "domains"
    form_class = FormDomain
    template_name = "universal.html"

    def get_queryset(self):
        return self.user.domain_set

@login_required
def rm(request):
    #try:
    user = request.session.get('switched_user', request.user)

    domain = get_object_or_404(user.domain_set, id=request.POST['object_id'])
    if domain.owner == user:
        logging.info(_("Deleting domain %s") % domain.name)

        for subdomain in Domain.objects.filter(parent=domain):
            for app in subdomain.apps():
                if app.domains_count <= 1:
                    remove_app_preparation(app, remove_domains=False)
                    app.delete()
            subdomain.delete()

        for app in domain.apps():
            if app.domains_count <= 1:
                remove_app_preparation(app)
                app.delete()

        if config.handle_dns and domain.dns:
            pri_br = BindRequest(user, "master")
            pri_br.remove_zone(domain)
            pri_br.mod_config()
            pri_br.reload()

            if config.handle_dns_secondary:
                sec_br = BindRequest(user, "slave")
                sec_br.mod_config()
                sec_br.reload()

        domain.delete()

    return JsonResponse("OK", {1: ugettext("Domain was successfuly deleted")})
    #except Exception, e:
    #    return JsonResponse("KO", {1: ugettext("Error deleting domain")})


@login_required
def add(request):
    """
    Add domain of customer
    """
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if request.method == 'POST':
        form = FormDomain(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]

            object = form.save(commit=False)
            object.owner = u
            object.save()

            if config.handle_dns and object.dns:
                pri_br = BindRequest(u, "master")
                pri_br.mod_zone(object)
                pri_br.mod_config()
                pri_br.reload()
                if config.handle_dns_secondary:
                    sec_br = BindRequest(u, "slave")
                    sec_br.mod_config()
                    sec_br.reload()

            logging.info(_("Added domain %s ") % name)
            message = _("Domain %s has been successfuly added") % name
            send_mail(_('Added new domain: %s') % name, message, settings.EMAIL_FROM, [mail for (name, mail) in settings.ADMINS if mail], fail_silently=True)

            messages.add_message(request, messages.SUCCESS, _('Domain has been added'))
            return HttpResponseRedirect(reverse("subdomains", args=(object.id, )))
    else:
        form = FormDomain()

    return render_to_response('universal.html',
            {
            "form": form,
            'form_helper': RostiFormHelper(),
            "title": _("Add domain"),
            "u": u,
            "superuser": superuser,
            "menu_active": "domains",
            },
        context_instance=RequestContext(request)
    )

@login_required
def subdomains(request, domain_id):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    domain = get_object_or_404(u.domain_set, id=int(domain_id))

    return render_to_response('old/subdomains.html',
            {
                "domain": domain,
                "u": u,
                "superuser": superuser,
                "menu_active": "domains",
            },
        context_instance=RequestContext(request)
    )

@login_required
def subdomains_list(request, domain_id):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    domain = get_object_or_404(u.domain_set, id=int(domain_id))

    if request.GET.get("subdomain_name"):
        for name in request.GET.get("subdomain_name").split(","):
            # TODO: check for duplication
            subdomain = Domain()
            subdomain.name = name.strip()
            subdomain.serial = 0
            subdomain.dns = False
            subdomain.mail = False
            subdomain.ipv4 = False
            subdomain.ipv6 = False
            subdomain.parent = domain
            subdomain.owner = u
            subdomain.save()
    elif request.GET.get("subdomain_id"):
        subdomain = get_object_or_404(u.domain_set, id=request.GET.get("subdomain_id"))
        for app in subdomain.apps():
            if app.domains_count <= 1:
                remove_app_preparation(app, remove_domains=False)
                app.delete()
        subdomain.delete()

    return render_to_response('old/subdomains_list.html',
            {
                "domain": domain,
                "subdomains": Domain.objects.filter(parent=domain),
                "u": u,
                "superuser": superuser,
                "menu_active": "domains",
            },
        context_instance=RequestContext(request)
    )

