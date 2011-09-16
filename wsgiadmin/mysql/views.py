# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from wsgiadmin.mysql.models import *
from wsgiadmin.keystore.tools import *
from wsgiadmin.requests.request import MySQLRequest
from wsgiadmin.useradmin.forms import simple_passwd

@login_required
def show(request, p=1):
    """
    Vylistování seznamu databází
    """
    p = int(p)
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    dbs = u.mysqldb_set.all()

    paginator = Paginator([x.dbname for x in dbs], 10)

    if not paginator.count:
        page = None
    else:
        page = paginator.page(p)

    return render_to_response('mysql.html',
            {
            "dbs": page,
            "paginator": paginator,
            "num_page": p,
            "u": u,
            "superuser": superuser,
            "menu_active": "dbs",
            }, context_instance=RequestContext(request))


@login_required
def add(request):
    """
    Vytvoření databáze
    """
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if request.method == 'POST':
        form = form_db(request.POST)
        form.u = u
        if form.is_valid():
            db = "%s_%s" % (u.parms.prefix(), form.cleaned_data["database"])

            m = mysqldb()
            m.dbname = db
            m.owner = u
            m.save()

            mr = MySQLRequest(u, u.parms.mysql_machine)
            mr.add_db(db, form.cleaned_data["password"])

            return HttpResponseRedirect(reverse("wsgiadmin.mysql.views.show"))
    else:
        form = form_db()
        form.u = u

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Vytvoření MySQL databáze"),
            "submit": _(u"Vytvořit databázi"),
            "action": reverse("wsgiadmin.mysql.views.add"),
            "u": u,
            "superuser": superuser,
            "menu_active": "dbs",
            },
                              context_instance=RequestContext(request)
    )


@login_required
@csrf_exempt
def passwd(request, db):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if request.method == "POST":
        form = simple_passwd(request.POST)

        if form.is_valid():
            if u.mysqldb_set.filter(dbname=db):
                mr = MySQLRequest(u, u.parms.mysql_machine)
                mr.passwd_db(db, form.cleaned_data["password"])
                return HttpResponse("OK")

    else:
        form = simple_passwd()

    return render_to_response('simplepasswd.html',
            {
            "form": form,
            "title": _(u"Heslo k mysql databázi %s") % db,
            "submit": _(u"Změni heslo"),
            "action": reverse("wsgiadmin.mysql.views.passwd", args=[db]),
            "u": u,
            "superuser": superuser,
            "menu_active": "dbs",
            },
                              context_instance=RequestContext(request)
    )


@login_required
@csrf_exempt
def rm(request, db):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    m = u.mysqldb_set.filter(dbname=db)
    if not m:
        return HttpResponse("Chyba při vykonávání operace")

    mr = MySQLRequest(u, u.parms.mysql_machine)
    mr.remove_db(db)
    m[0].delete()
    return HttpResponse("Databáze vymazána")
