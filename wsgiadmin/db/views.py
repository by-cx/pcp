# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.decorators.csrf import csrf_exempt
from wsgiadmin.apacheconf.views import JsonResponse

from wsgiadmin.db.forms import PgsqlForm, MysqlForm
from wsgiadmin.keystore.tools import *
from wsgiadmin.requests.request import MySQLRequest, PostgreSQLRequest
from wsgiadmin.useradmin.forms import PasswordForm


@login_required
def show(request, dbtype=None, page=1):
    """
    Vylistování seznamu databází
    """
    p = int(page)
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if dbtype == 'mysql':
        dbs = u.mysqldb_set.all()
    else:
        dbs = u.pgsql_set.all()

    paginator = Paginator([x.dbname for x in dbs], 10)
    if not paginator.count:
        page = None
    else:
        page = paginator.page(p)

    return render_to_response('db.html',
            {
            'dbtype': dbtype,
            "dbs": page,
            "paginator": paginator,
            "num_page": p,
            "u": u,
            "superuser": superuser,
            "menu_active": "dbs",
            }, context_instance=RequestContext(request))


@login_required
def add(request, dbtype):
    """
    Vytvoření databáze
    """
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    form_class = [PgsqlForm, MysqlForm][dbtype == 'mysql']

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            db_obj = form.save(commit=False)
            db_obj.owner = u
            db_obj.dbname = "%s_%s" % (u.parms.prefix(), db_obj.dbname)
            db_obj.save()


            if dbtype == 'mysql':
                mr = MySQLRequest(u, u.parms.mysql_machine)
            elif dbtype == 'pgsql':
                mr = PostgreSQLRequest(u, u.parms.pgsql_machine)

            mr.add_db(db_obj.dbname, form.cleaned_data["password"])

            return HttpResponseRedirect(reverse("wsgiadmin.db.views.show", kwargs=dict(dbtype=dbtype)))
    else:
        form = form_class()
        form.owner = u

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Vytvoření %s databáze" % dbtype),
            "submit": _(u"Vytvořit databázi"),
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
                m = u.mysqldb_set.get(dbname=dbname)
                mr = MySQLRequest(u, u.parms.mysql_machine)
            elif dbtype == 'pgsql':
                m = u.pgsqldb_set.get(dbname=dbname)
                mr = PostgreSQLRequest(u, u.parms.pgsql_machine)

            mr.passwd_db(dbname, dbname)
            return HttpResponseRedirect(reverse('db_list', kwargs=dict(dbtype=dbtype)))
    else:
        form = PasswordForm()


    return render_to_response('simplepasswd.html',
            {
            'dbtype': dbtype,
            "form": form,
            "dbname": dbname,
            "title": _(u"Password for database %s") % dbname,
            "submit": _(u"Change password"),
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
        dbname = request.POST['dbname']
        u = request.session.get('switched_user', request.user)
        superuser = request.user
        if dbtype == 'mysql':
            m = u.mysqldb_set.get(dbname=dbname)
            mr = MySQLRequest(u, u.parms.mysql_machine)
        elif dbtype == 'pgsql':
            m = u.pgsqldb_set.get(dbname=dbname)
            mr = PostgreSQLRequest(u, u.parms.pgsql_machine)

        mr.remove_db(dbname)
        m.delete()

        return JsonResponse("OK", {1: ugettext("Database was sucesfuly deleted")})
    except Exception, e:
        return JsonResponse("KO", {1: e})
