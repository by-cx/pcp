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

from wsgiadmin.domains.forms import RegistrationRequestForm
from wsgiadmin.domains.models import Domain
from wsgiadmin.requests.request import BindRequest
from wsgiadmin.service.forms import RostiFormHelper
from wsgiadmin.service.views import JsonResponse, RostiListView


class DomainsListView(RostiListView):

    menu_active = 'domains'
    template_name = 'domains.html'
    delete_url_reverse = 'domain_remove'

    def get_queryset(self):
        return self.user.domain_set.all()


@login_required
def rm(request):

    try:
        u = request.session.get('switched_user', request.user)

        d = get_object_or_404(Domain, id=request.POST['object_id'])
        if d.owner == u:
            logging.info(_("Deleting domain %s") % d.name)

            if config.handle_dns and d.dns:
                pri_br = BindRequest(u, "master")
                pri_br.remove_zone(d)
                pri_br.mod_config()
                pri_br.reload()

                sec_br = BindRequest(u, "slave")
                sec_br.mod_config()
                sec_br.reload()

            d.delete()

        return JsonResponse("OK", {1: ugettext("Domain was successfuly deleted")})
    except Exception, e:
        return JsonResponse("KO", {1: ugettext("Error deleting domain")})


@login_required
def add(request):
    """
    Add domain of customer
    """
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if request.method == 'POST':
        form = RegistrationRequestForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["domain"]

            instance, created = Domain.objects.get_or_create(name=name, owner=u)

            if config.handle_dns and instance.dns:
                pri_br = BindRequest(u, "master")
                pri_br.mod_zone(instance)
                pri_br.mod_config()
                pri_br.reload()
                sec_br = BindRequest(u, "slave")
                sec_br.mod_config()
                sec_br.reload()

            logging.info(_("Added domain %s ") % name)
            message = _("Domain %s has been successfuly added") % name
            send_mail(_('Added new domain: %s') % name, message, settings.EMAIL_FROM, [mail for (name, mail) in settings.ADMINS if mail], fail_silently=True)

            messages.add_message(request, messages.SUCCESS, _('Domain has been added'))
            return HttpResponseRedirect(reverse("domains_list"))
    else:
        form = RegistrationRequestForm()

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
