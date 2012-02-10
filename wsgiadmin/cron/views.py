from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from wsgiadmin.cron.forms import FormCron
from wsgiadmin.requests.request import SystemRequest
from wsgiadmin.service.views import RostiListView, RostiUpdateView, RostiCreateView
from wsgiadmin.cron.models import Cron
from wsgiadmin.service.views import JsonResponse
from django.utils.translation import ugettext_lazy as _, ugettext

class CronListView(RostiListView):
    menu_active = 'webapps'
    template_name = 'cron.html'
    delete_url_reverse = 'remove_cron'

    def get_queryset(self):
        return self.user.cron_set.all()

class CronUpdateView(RostiUpdateView):
    menu_active = 'webapps'
    success_url = "/cron/list/"
    form_class = FormCron
    template_name = "universal.html"

    def get_object(self, queryset=None):
        return self.user.cron_set.get(id=int(self.kwargs.get("pk")))

    def form_valid(self, form):
        ret = super(CronUpdateView, self).form_valid(form)
        sr = SystemRequest(self.user, self.user.parms.web_machine)
        sr.cron(self.user)
        messages.add_message(self.request, messages.SUCCESS, _('Cron record has been updated'))
        return ret

class CronCreateView(RostiCreateView):
    menu_active = 'webapps'
    template_name="universal.html"
    form_class=FormCron
    success_url = "/cron/list/"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user

        ret =  super(CronCreateView, self).form_valid(form)

        sr = SystemRequest(self.user, self.user.parms.web_machine)
        sr.cron(self.user)
        messages.add_message(self.request, messages.SUCCESS, _('Cron record has been created'))

        return ret


@login_required
def remove_cron(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    try:
        cron = request.user.cron_set.get(id=int(request.POST.get("object_id")))
        cron.delete()
        sr = SystemRequest(request.user, request.user.parms.web_machine)
        sr.cron(request.user)
        return JsonResponse("OK", {1: ugettext("Cron record was successfuly removed")})
    except Exception, e:
        return JsonResponse("KO", {1: ugettext("Error deleting cron record")})