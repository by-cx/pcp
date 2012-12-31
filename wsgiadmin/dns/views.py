from constance import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from wsgiadmin.dns.forms import RecordForm, DomainForm, DomainUpdateForm
from wsgiadmin.dns.models import Domain, Record
from wsgiadmin.dns.server import DomainObject
from wsgiadmin.dns.utils import set_domain_default_state
from django.utils.translation import ugettext_lazy as _


class DomainsListView(ListView):
    menu_active = "dns"
    model = Domain
    template_name = "dns/list.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(DomainsListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(DomainsListView, self).get_queryset()
        queryset = queryset.filter(user=self.user).order_by("name")
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DomainsListView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


class DomainCreateView(CreateView):
    form_class = DomainForm
    menu_active = "dns"
    template_name = "universal.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(DomainCreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.user
        self.object.nss = config.dns_default_nss
        self.object.save()
        set_domain_default_state(self.object)

        script = DomainObject()
        script.update(self.object)
        script.reload()
        script.commit()

        messages.add_message(self.request, messages.SUCCESS, _('Domain has been created'))

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("dns_editor", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(DomainCreateView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


class DomainUpdateView(UpdateView):
    form_class = DomainUpdateForm
    menu_active = "dns"
    template_name = "universal.html"
    model = Domain

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(DomainUpdateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super(DomainUpdateView, self).form_valid(form)
        script = DomainObject()
        script.update(self.object)
        script.reload()
        script.commit()

        messages.add_message(self.request, messages.SUCCESS, _('Domain has been updated'))

        return response

    def get_success_url(self):
        return reverse("dns_list")

    def get_context_data(self, **kwargs):
        context = super(DomainUpdateView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


class EditorView(TemplateView):
    template_name = "dns/editor.html"
    menu_active = "dns"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(EditorView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context.get("form")
        if form.is_valid():
            record = form.save(commit=False)
            record.user = self.user
            record.domain = self.get_domain()
            record.save()

            script = DomainObject()
            script.update(self.get_domain())
            script.reload()
            script.commit()

            messages.add_message(request, messages.SUCCESS, _('Record has been created'))

            return HttpResponseRedirect(reverse("dns_editor", kwargs={"pk": self.kwargs.get("pk")}))
        return self.render_to_response(context)

    def get_form(self):
        record = self.get_record()
        if self.request.method == "POST":
            if record:
                return RecordForm(self.request.POST, instance=record)
            return RecordForm(self.request.POST)
        if record:
            return RecordForm(instance=record)
        return RecordForm()

    def get_record(self):
        if self.request.GET.get("record_pk"):
            return Record.objects.filter(domain=self.get_domain()).get(id=self.request.GET.get("record_pk"))
        return None

    def get_domain(self):
         return self.user.dns_set.get(id=self.kwargs.get("pk"))

    def get_records(self):
        return Record.objects.filter(domain=self.get_domain()).order_by("order_num")

    def get_context_data(self, **kwargs):
        context = super(EditorView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['domain'] = self.get_domain()
        context['records'] = self.get_records()
        context['form'] = self.get_form()
        return context


def rm_domain(request):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    domain_id = int(request.GET.get("domain_pk"))
    domain = user.dns_set.get(id=domain_id)
    domain.delete()

    script = DomainObject()
    script.update()
    script.uninstall(domain)
    script.reload()
    script.commit()

    messages.add_message(request, messages.SUCCESS, _('Domain has been removed'))

    return HttpResponseRedirect(reverse("dns_list"))


def rm_record(request):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    record_id = int(request.GET.get("record_pk"))
    record = Record.objects.filter(domain__user=user).get(id=record_id)
    domain = record.domain
    record.delete()

    messages.add_message(request, messages.SUCCESS, _('Record has been removed from the zone'))

    return HttpResponseRedirect(reverse("dns_editor", kwargs={"pk": domain.id}))


def record_order(request, domain_pk):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    domain = user.dns_set.get(id=domain_pk)
    for index, record_id in enumerate(request.GET.get("records").split(",")):
        record = domain.record_set.get(id=record_id)
        record.order_num = index + 1
        record.save()
        #TODO: make a new config files for bind
    return HttpResponse("OK")


def new_configuration(request, domain_pk):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    domain = user.dns_set.get(id=domain_pk)

    script = DomainObject()
    script.update(domain)
    script.reload()
    script.commit()

    messages.add_message(request, messages.SUCCESS, _('Configuration has been send to the NS servers.'))

    return HttpResponseRedirect(reverse("dns_editor", kwargs={"pk": domain.id}))
