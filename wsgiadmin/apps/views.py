import crypt
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView, CreateView, UpdateView
from wsgiadmin.apps.forms import AppForm, AppStaticForm, AppPHPForm, AppNativeForm, AppProxyForm, AppPythonForm, DbForm, DbFormPasswd, FtpAccessForm
from wsgiadmin.apps.models import App, Db, FtpAccess
from wsgiadmin.apps.backend import PythonApp, typed_object, DbObject, AppBackend
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from django.contrib import messages
from wsgiadmin.core.utils import server_chooser, get_load_balancers


class AppsListView(ListView):
    menu_active = "apps"
    model = AppBackend
    template_name = "apps/apps.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(AppsListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(AppsListView, self).get_queryset()
        queryset = queryset.filter(user=self.user).order_by("name")
        return queryset

    def get_context_data(self, **kwargs):


        context = super(AppsListView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


class AppDetailView(TemplateView):
    model = App
    menu_active = "apps"
    template_name = "apps/app_info.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(AppDetailView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        app_id = self.kwargs.get("app_id")
        if not app_id:
            raise Http404
        app = self.model.objects.get(id=app_id, user=self.user)
        return typed_object(app)

    def get_context_data(self, **kwargs):
        context = super(AppDetailView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['app'] = self.get_object()
        context['dbs'] = context['app'].db_set.all()
        context['ftps'] = context['app'].ftpaccess_set.all()
        context['loadbalancers'] = get_load_balancers()
        return context


class AppParametersView(TemplateView):
    menu_active = "apps"
    app_type = None
    template_name = "universal.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.get_form()(request.POST)
        app = self.get_object()
        if app.app_type == "python":
            form.fields["python"].choices = [(python.name, python.name) for python in self.get_object().core_server.pythoninterpreter_set.all()]
        if form.is_valid():
            parms = {}
            for field in form.cleaned_data:
                if field == "domains":
                    app.domains = form.cleaned_data[field]
                elif field == "password":
                    continue
                else:
                    parms[field] = form.cleaned_data[field]
            app.parameters = parms
            app.save()

            # communication with server
            if not app.disabled:
                if not app.installed:
                    app.install()
                app.update()
                if app.app_type == "python":
                    app.restart()
                if form.cleaned_data["password"]:
                    app.passwd(form.cleaned_data["password"])
                app.commit()
                messages.add_message(request, messages.SUCCESS, _('Changes has been saved.'))
            else:
                messages.add_message(request, messages.WARNING, _('Changes has been saved. But app is disabled.'))
            return HttpResponseRedirect(reverse("app_detail", kwargs={"app_id": app.id}))
        context["form"] = form
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.get_form()(initial=self.get_initial())
        if self.get_object().app_type == "python":
            form.fields["python"].choices = [(python.name, python.name) for python in self.get_object().core_server.pythoninterpreter_set.all()]
        context["form"] = form
        return self.render_to_response(context)

    def get_autocomplete_list(self):
        return []

    def get_form(self):
        if self.app_type == "static":
            form = AppStaticForm
        elif self.app_type == "php":
            form = AppPHPForm
        elif self.app_type == "phpfpm":
            form = AppPHPForm
        elif self.app_type == "python":
            form = AppPythonForm
        elif self.app_type == "native":
            form = AppNativeForm
        elif self.app_type == "proxy":
            form = AppProxyForm
        else:
            raise Http404
        form.this_app = self.get_object()
        return form

    def get_initial(self):
        initial = {"domains": self.get_object().domains}
        initial.update(self.get_object().parameters)
        return initial

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(AppParametersView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        app_id = self.kwargs.get("app_id")
        if not app_id:
            raise Http404
        app = self.user.app_set.get(id=app_id)
        return typed_object(app)

    def get_context_data(self, **kwargs):
        context = super(AppParametersView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['app'] = self.get_object()
        context["title"] = __("Settings of the %s app") % self.get_object().name
        context['form'] = self.get_form()
        context['autocomplete_list'] = self.get_autocomplete_list()
        return context


class AppCreateView(CreateView):
    form_class = AppForm
    app_type = None
    template_name = "universal.html"
    model = App
    menu_active = "apps"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(AppCreateView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        form = super(AppCreateView, self).get_form(form_class)
        form.user = self.user
        form.fields["core_server"].queryset = server_chooser(self.app_type, hidden=False, user=self.user)
        return form

    def get_success_url(self):
        if self.app_type == "static":
            return reverse("app_params_static", kwargs={"app_id": self.object.id})
        elif self.app_type == "php":
            return reverse("app_params_php", kwargs={"app_id": self.object.id})
        elif self.app_type == "phpfpm":
            return reverse("app_params_phpfpm", kwargs={"app_id": self.object.id})
        elif self.app_type == "python":
            return reverse("app_params_python", kwargs={"app_id": self.object.id})
        elif self.app_type == "native":
            return reverse("app_params_native", kwargs={"app_id": self.object.id})
        elif self.app_type == "proxy":
            return reverse("app_params_proxy", kwargs={"app_id": self.object.id})
        else:
            return reverse("apps_list")

    def form_valid(self, form):
        success_url = super(AppCreateView, self).form_valid(form)
        self.object.user = self.user
        self.object.app_type = self.app_type
        self.object.save()
        return success_url

    def get_context_data(self, **kwargs):
        context = super(AppCreateView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


class FtpAccessCreateView(CreateView):
    form_class = FtpAccessForm
    template_name = "universal.html"
    model = FtpAccess
    menu_active = "apps"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        self.success_url = reverse("app_detail", kwargs={"app_id": request.GET.get("app_id")})
        return super(FtpAccessCreateView, self).dispatch(request, *args, **kwargs)

    def get_app(self):
        app_id = self.request.GET.get("app_id")
        return self.user.app_set.get(id=app_id)

    def get_form(self, form_class):
        backend = AppBackend.objects.get(id=self.get_app().id)
        form = super(FtpAccessCreateView, self).get_form(form_class)
        form.fields["directory"].choices = form.fields["directory"].choices = [("", _("App root"))]+[(x, x) for x in backend.get_directories() if x]
        form.app = self.get_app()
        return form

    def form_valid(self, form):
        object = form.save(commit=False)
        backend = AppBackend.objects.get(id=self.get_app().id)
        object.app = self.get_app()
        object.hash = crypt.crypt(form.cleaned_data["password"], self.user.username)
        object.home = backend.get_home()
        object.uid = backend.get_uid()
        object.gid = backend.get_gid()
        object.save()
        return super(FtpAccessCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FtpAccessCreateView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


class FtpAccessUpdateView(UpdateView):
    form_class = FtpAccessForm
    template_name = "universal.html"
    model = FtpAccess
    menu_active = "apps"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(FtpAccessUpdateView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(FtpAccessUpdateView, self).get_queryset()
        queryset = queryset.filter(app__user=self.user)
        return queryset

    def get_app(self):
        return AppBackend.objects.get(id=self.object.app.id)

    def get_form(self, form_class):
        form = super(FtpAccessUpdateView, self).get_form(form_class)
        form.fields["directory"].choices = [("", _("App root"))]+[(x, x) for x in self.get_app().get_directories() if x]
        form.fields["password"].required = False
        form.app = self.get_app()
        form.ftpaccess = self.object
        return form

    def form_valid(self, form):
        self.success_url = reverse("app_detail", kwargs={"app_id": self.get_object().app_id})
        ftpaccess = form.save(commit=False)
        ftpaccess.username = form.cleaned_data["username"]
        ftpaccess.directory = form.cleaned_data["directory"]
        if form.cleaned_data["password"]:
            ftpaccess.hash = crypt.crypt(form.cleaned_data["password"], self.user.username)
        ftpaccess.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(FtpAccessUpdateView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


class DbCreateView(CreateView):
    form_class = DbForm
    template_name = "universal.html"
    model = Db
    menu_active = "apps"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        self.success_url = reverse("app_detail", kwargs={"app_id": request.GET.get("app_id")})
        return super(DbCreateView, self).dispatch(request, *args, **kwargs)

    def get_app(self):
        app_id = self.request.GET.get("app_id")
        return self.user.app_set.get(id=app_id)

    def form_valid(self, form):
        object = form.save(commit=False)
        object.app = self.get_app()
        object.save()
        db = DbObject.objects.get(id=object.id)
        db.install()
        db.commit()
        return super(DbCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(DbCreateView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


class DbUpdateView(UpdateView):
    form_class = DbFormPasswd
    template_name = "universal.html"
    model = Db
    menu_active = "apps"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(DbUpdateView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(DbUpdateView, self).get_queryset()
        queryset = queryset.filter(app__user=self.user)
        return queryset

    def form_valid(self, form):
        self.success_url = reverse("app_detail", kwargs={"app_id": self.get_object().app_id})
        success = super(DbUpdateView, self).form_valid(form)
        object = DbObject.objects.get(id=self.object.id)
        object.passwd(object.password)
        object.commit()
        return success

    def get_context_data(self, **kwargs):
        context = super(DbUpdateView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['u'] = self.user
        context['superuser'] = self.request.user
        return context


@login_required()
def db_rm(request):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    db_id = int(request.GET.get("db_id"))
    db = Db.objects.filter(app__user=user).get(id=db_id)
    db = DbObject.objects.get(id=db.id)
    db.uninstall()
    db.commit()
    app_id = db.app_id
    db.delete()
    messages.add_message(request, messages.SUCCESS, _('Database has been removed'))
    return HttpResponseRedirect(reverse("app_detail", kwargs={"app_id": app_id}))

@login_required()
def ftp_rm(request):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    ftpaccess_id = int(request.GET.get("ftpaccess_id"))
    ftpaccess = FtpAccess.objects.filter(app__user=user).get(id=ftpaccess_id)
    app_id = ftpaccess.app_id
    ftpaccess.delete()
    messages.add_message(request, messages.SUCCESS, _('FTP access has been removed'))
    return HttpResponseRedirect(reverse("app_detail", kwargs={"app_id": app_id}))


@login_required()
def app_rm(request):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    app_id = int(request.GET.get("app_id"))
    app = get_object_or_404(user.app_set, id=app_id)
    app = typed_object(app)

    #databases
    for db in app.db_set.all():
        db = DbObject.objects.get(id=db.id)
        db.uninstall()
        db.commit()
        db.delete()

    #app
    app.uninstall()
    app.commit()
    app.delete()
    messages.add_message(request, messages.SUCCESS, _('App has been removed'))
    return HttpResponseRedirect(reverse("apps_list"))


@login_required()
def app_restart(request):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    app_id = int(request.GET.get("app_id"))
    app = get_object_or_404(user.app_set, id=app_id)
    if app.app_type == "python" and not app.disabled:
        app = PythonApp.objects.get(id=app.id)
        app.update()
        app.restart()
        app.commit()
        messages.add_message(request, messages.SUCCESS, _('App has been restarted'))
    elif app.disabled:
        messages.add_message(request, messages.WARNING, _('App is disabled'))
    else:
        messages.add_message(request, messages.ERROR, _('App is not resetable'))
    return HttpResponseRedirect(reverse("app_detail", kwargs={"app_id": app.id}))
