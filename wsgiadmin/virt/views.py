from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from wsgiadmin.core.models import Server
from wsgiadmin.service.views import RostiListView, RostiCreateView
from wsgiadmin.virt.forms import VirtForm
from wsgiadmin.virt.models import VirtMachine
from wsgiadmin.virt.utils import VirtMachineConnection


class VirtListView(RostiListView):
    menu_active = "virt"
    template_name = "virt/list.html"
    model = VirtMachine

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
        return get_object_or_404(VirtMachineConnection, id=kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        #vm = self.get_vm(self.kwargs)
        context = super(VirtSummaryView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        context["vm"] = self.get_vm(kwargs)
        return context
