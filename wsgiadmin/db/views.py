from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _, ugettext

from wsgiadmin.db.forms import PgsqlForm, MysqlForm
from wsgiadmin.requests.request import MySQLRequest, PostgreSQLRequest
from wsgiadmin.service.views import JsonResponse, RostiListView
from wsgiadmin.useradmin.forms import PasswordForm


class DatabasesListView(RostiListView):

    menu_active = 'dbs'
    template_name = 'db.html'

    def get(self, request, *args, **kwargs):
        if kwargs.get('dbtype', None) not in ('mysql', 'pgsql'):
            #TODO - move default list into settings
            return HttpResponseRedirect(reverse('db_list', kwargs={'dbtype': 'mysql'}))

        return super(DatabasesListView, self).get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        if self.kwargs['dbtype'] == 'mysql':
            return self.user.mysqldb_set.all()
        else:
            return self.user.pgsql_set.all()


    def get_context_data(self, **kwargs):
        context = super(DatabasesListView, self).get_context_data(**kwargs)
        context['menu_active'] = self.menu_active
        context['dbtype'] = self.kwargs['dbtype']
        return context


@login_required
def add(request, dbtype):
    """
    DB create
    """
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    form_class = [PgsqlForm, MysqlForm][dbtype == 'mysql']

    if request.method == 'POST':
        form = form_class(request.POST)
        orig_dbname = form.data['dbname']
        form.data['dbname'] = "%s_%s" % (u.parms.prefix(), form.data['dbname'])

        if form.is_valid():
            db_obj = form.save(commit=False)
            db_obj.owner = u
            db_obj.save()

            if dbtype == 'mysql':
                mr = MySQLRequest(u, u.parms.mysql_machine)
            elif dbtype == 'pgsql':
                mr = PostgreSQLRequest(u, u.parms.pgsql_machine)
            else:
                return HttpResponseServerError(_('Unknown database type'))
            mr.add_db(db_obj.dbname, form.cleaned_data["password"])

            return HttpResponseRedirect(reverse("db_list", kwargs=dict(dbtype=dbtype)))
        else:
            form.data['dbname'] = orig_dbname
    else:
        form = form_class()
        form.owner = u

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _("Create %s database" % dbtype),
            "submit": _("Create database"),
            "action": reverse("db_add", kwargs=dict(dbtype=dbtype)),
            "u": u,
            "superuser": superuser,
            "menu_active": "dbs",
            },
        context_instance=RequestContext(request)
    )


@login_required
def passwd(request, dbtype, dbname):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            if dbtype == 'mysql':
                #TODO - raise better exception
                m = u.mysqldb_set.get(dbname=dbname)
                mr = MySQLRequest(u, u.parms.mysql_machine)
            elif dbtype == 'pgsql':
                m = u.pgsqldb_set.get(dbname=dbname)
                mr = PostgreSQLRequest(u, u.parms.pgsql_machine)
            else:
                return HttpResponseServerError(_('Unknown database type'))

            mr.passwd_db(dbname, dbname)
            messages.add_message(request, messages.SUCCESS, _('Password has been changed'))
            return HttpResponseRedirect(reverse('db_list', kwargs=dict(dbtype=dbtype)))
    else:
        form = PasswordForm()

    return render_to_response('simplepasswd.html',
            {
            'dbtype': dbtype,
            "form": form,
            "dbname": dbname,
            "title": _("Password for database %s") % dbname,
            "submit": _("Change password"),
            "action": reverse("db_passwd", kwargs=dict(dbtype=dbtype, dbname=dbname)),
            "u": u,
            "superuser": superuser,
            "menu_active": "dbs",
            },
        context_instance=RequestContext(request)
    )


@login_required
def rm(request, dbtype):
    try:
        object_id = request.POST['object_id']
        u = request.session.get('switched_user', request.user)

        if dbtype == 'mysql':
            m = u.mysqldb_set.get(pk=object_id)
            mr = MySQLRequest(u, u.parms.mysql_machine)
        elif dbtype == 'pgsql':
            m = u.pgsqldb_set.get(pk=object_id)
            mr = PostgreSQLRequest(u, u.parms.pgsql_machine)
        else:
            raise Exception(ugettext('Unknown database type'))

        mr.remove_db(m.dbname)
        m.delete()

        return JsonResponse("OK", {1: ugettext("Database was successfuly deleted")})
    except Exception, e:
        return JsonResponse("KO", {1: ugettext("Error during delete database")})
