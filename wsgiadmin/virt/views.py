from wsgiadmin.core.models import Server
from wsgiadmin.service.views import RostiListView, RostiCreateView
from wsgiadmin.virt.forms import VirtForm
from wsgiadmin.virt.models import VirtMachine


class VirtListView(RostiListView):
    menu_active = "virt"
    template_name = "virt/list.html"
    model = VirtMachine

    def get_queryset(self):
        queryset = super(VirtListView, self).get_queryset()
        queryset = queryset.filter(user=self.user)
        return queryset

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
