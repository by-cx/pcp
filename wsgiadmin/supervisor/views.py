from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from wsgiadmin.service.views import RostiCreateView, RostiListView, RostiUpdateView, JsonResponse
from wsgiadmin.supervisor.forms import FormProgram
from django.utils.translation import ugettext_lazy as _

class CreateProgram(RostiCreateView):
    menu_active = "supervisor"
    form_class = FormProgram

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.user
        self.object.save()
        return super(CreateProgram, self).form_valid(form)

class ListProgram(RostiListView):
    menu_active = "supervisor"

    def get_queryset(self):
        return self.user.program_set

class UpdateProgram(RostiUpdateView):
    menu_active = "supervisor"
    form_class = FormProgram

    def get_queryset(self):
        return self.user.program_set

@login_required
def rm(request):
    try:
        u = request.session.get('switched_user', request.user)
        p = get_object_or_404(u.program_set, id=request.POST['object_id'])
        p.delete()

        return JsonResponse("OK", {1: _("Program was successfuly deleted")})
    except Exception, e:
        return JsonResponse("KO", {1: _("Error deleting program")})
