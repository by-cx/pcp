from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from wsgiadmin.core.models import Server
from wsgiadmin.service.views import RostiListView, RostiCreateView
from wsgiadmin.virt.backend import VirtMachineBackend
from wsgiadmin.virt.forms import VirtForm
from wsgiadmin.virt.models import VirtMachine, VirtVariant
from wsgiadmin.virt.utils import VirtMachineConnection


class VirtListView(RostiListView):
    menu_active = "virt"
    template_name = "virt/list.html"
    model = VirtMachineConnection

    def get_queryset(self):
        queryset = super(VirtListView, self).get_queryset()
        queryset = queryset.filter(user=self.user)
        return queryset

    def get_context_data(self, **kwargs):
        return super(VirtListView, self).get_context_data(**kwargs)


class VirtCreateView(RostiCreateView):
    model = VirtMachine
    menu_active = "virt"
    template_name = "universal.html"
    form_class = VirtForm

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.user
        object.server = Server.objects.filter(virt=True)[0]
        object.save()


class VirtSummaryView(TemplateView):
    template_name = "virt/summary.html"
    menu_active = "virt"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(VirtSummaryView, self).dispatch(request, *args, **kwargs)

    def get_vm(self, kwargs):
        return get_object_or_404(VirtMachineConnection, id=kwargs.get("pk"), user=self.user)

    def get_context_data(self, **kwargs):
        #vm = self.get_vm(self.kwargs)
        context = super(VirtSummaryView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        context["vm"] = self.get_vm(kwargs)
        return context


class VirtNewView(TemplateView):
    template_name = "virt/new_vm.html"
    menu_active = "virt"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(VirtNewView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        #vm = self.get_vm(self.kwargs)
        context = super(VirtNewView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


class VirtCreateView(RostiCreateView):
    template_name = "universal.html"
    menu_active = "virt"
    form_class = VirtForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(VirtNewView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.user
        object.server = Server.objects.filter(virt=True)[0] #TODO: make it better
        object.save()

        variant = VirtVariant.objects.get(id=self.request.GET.get())
        virt_machine = VirtMachineConnection.objects.get(id=object.id)
        virt_machine.create_domain(variant.memory, variant.cpus, variant.disk_size)

        backend = VirtMachineBackend.objects.get(id=virt_machine.id)
        backend.install()

        return HttpResponseRedirect(reverse("virt_list"))

    def get_context_data(self, **kwargs):
        #vm = self.get_vm(self.kwargs)
        context = super(VirtNewView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


@login_required()
def virt_state_changer(request, pk, state):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    vm = get_object_or_404(VirtMachineConnection, id=pk, user=user)
    if state == "start":
        vm.start()
    elif state == "reset":
        vm.reset()
    elif state == "reboot":
        vm.reboot()
    elif state == "shutdown":
        vm.shutdown()
    elif state == "force_shutdown":
        vm.force_shutdown()

    return HttpResponseRedirect(reverse("virt_summary", kwargs={"pk": pk}))


def backend_install(request, pk):
    user = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser():
        return HttpResponseForbidden('You are not superuser')

    backend = get_object_or_404(VirtMachineBackend, id=pk)
    backend.install()

    return HttpResponseRedirect(reverse("virt_summary", kwargs={"pk": pk}))