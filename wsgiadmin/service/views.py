import anyjson
from constance import config

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _

class JsonResponse(HttpResponse):
    def __init__(self, result, messages):
        content = anyjson.serialize(dict(result=result, messages=messages))
        super(JsonResponse, self).__init__(content, content_type='application/jsonrequest')


class RostiListView(ListView):
    menu_active = ""
    paginate_by = config.pagination
    delete_url_reverse = ""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(RostiListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RostiListView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        if self.delete_url_reverse:
            context['delete_url'] = reverse(self.delete_url_reverse)
        return context

class RostiCreateView(CreateView):
    menu_active = ""
    form_class = None
    form_action = '.'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(RostiCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RostiCreateView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['submit'] = _("Create")
        if 'action' not in context:
            context['action'] = self.form_action
        return context


class RostiUpdateView(UpdateView):
    menu_active = ""
    form_class = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(RostiUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RostiUpdateView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['submit'] = _("Update")
        return context
