# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.core.paginator import Paginator

from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as user
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from wsgiadmin.bills.models import income

from wsgiadmin.invoices.geninvoice import *
from wsgiadmin.invoices.models import invoice, item
from wsgiadmin.clients.models import *

from django.utils.translation import ugettext_lazy as _

import datetime

@login_required
def show(request, p=1):
    """
       Vylistování seznamu databází
   """
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    p = int(p)

    data = list(invoice.objects.order_by("payment_id"))
    data.reverse()
    paginator = Paginator(data, 50)

    if not paginator.count:
        page = None
    else:
        page = paginator.page(p)

    total_not_pay = 0
    not_payed = []
    for iinvoice in invoice.objects.filter(payed=False):
        total_not_pay += iinvoice.totalInt()
        not_payed.append(iinvoice)

    years = [x for x in range(2009, datetime.date.today().year + 1)]
    total_years = {}
    for year in years:
        total = 0
        for iinvoice in invoice.objects.filter(date_exposure__year=year):
            total += iinvoice.totalInt()
        total_years[year] = total

    return render_to_response('invoices.html',
            {
            "invoices": page,
            "paginator": paginator,
            "num_page": p,
            "u": u,
            "superuser": superuser,
            "total_not_pay": total_not_pay,
            "total_years": total_years,
            "not_payed": not_payed,
            "menu_active": "invoices",
            }, context_instance=RequestContext(request))


@login_required
def add_invoice(request):
    """
       Vytvoření faktury
   """
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    if request.method == 'POST':
        form = form_invoice(request.POST)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse("wsgiadmin.invoices.views.show"))
    else:
        form = form_invoice(initial={"payment_id": next_payment_id(request, False)})

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Přidání faktury"),
            "submit": _(u"Přidat fakturu"),
            "action": reverse("wsgiadmin.invoices.views.add_invoice"),
            "u": u,
            "superuser": superuser,
            "menu_active": "invoices",
            },
                              context_instance=RequestContext(request)
    )


@login_required
def update_invoice(request, iid):
    """
       Upravení faktury
    """
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")
    iinvoice = get_object_or_404(invoice, id=int(iid))

    if request.method == 'POST':
        form = form_invoice(request.POST, instance=iinvoice)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse("wsgiadmin.invoices.views.show"))
    else:
        form = form_invoice(instance=iinvoice)

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Upravení faktury"),
            "submit": _(u"Upravit fakturu"),
            "action": reverse("wsgiadmin.invoices.views.update_invoice",
                              args=[iid]),
            "u": u,
            "superuser": superuser,
            "menu_active": "invoices",
            },
                              context_instance=RequestContext(request)
    )


@login_required
def add_item(request, iid):
    """
       Vytvoření položky faktury

       integer iid - ID faktury
    """
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    iinvoice = get_object_or_404(invoice, id=int(iid))

    if request.method == 'POST':
        form = form_item(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.invoice = iinvoice
            instance.save()

            return HttpResponseRedirect(
                reverse("wsgiadmin.invoices.views.show"))
    else:
        form = form_item()

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Přidání položky faktury"),
            "submit": _(u"Přidat položku fakturu"),
            "action": reverse("wsgiadmin.invoices.views.add_item", args=[iid]),
            "u": u,
            "superuser": superuser,
            "menu_active": "invoices",
            },
                              context_instance=RequestContext(request)
    )


@login_required
def update_item(request, iid):
    """
       Upravení položky faktury

       integer iid - ID položky
   """
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")
    iitem = get_object_or_404(item, id=int(iid))

    if request.method == 'POST':
        form = form_item(request.POST, instance=iitem)
        if form.is_valid():
            instance = form.save()

            return HttpResponseRedirect(
                reverse("wsgiadmin.invoices.views.show"))
    else:
        form = form_item(instance=iitem)

    return render_to_response('universal.html',
            {
            "form": form,
            "title": _(u"Upravení položky faktury"),
            "submit": _(u"Upravit položku fakturu"),
            "action": reverse("wsgiadmin.invoices.views.update_item",
                              args=[iid]),
            "u": u,
            "superuser": superuser,
            "menu_active": "invoices",
            },
                              context_instance=RequestContext(request)
    )


@login_required
@csrf_exempt
def payback(request, iid):
    """
       Zaplacení faktury
   """
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    iinvoice = get_object_or_404(invoice, id=int(iid))
    iinvoice.payed = True
    iinvoice.save()

    parm = Parms.objects.filter(address=iinvoice.client_address)

    if parm:
        i = income()
        i.cash = iinvoice.totalInt()
        i.note = iinvoice.payment_id
        i.currency = "czk"
        i.user = parm[0].user
        i.save()

    return HttpResponse("Zaplaceno")


@login_required
@csrf_exempt
def rm(request, iid):
    """
   Smazání faktury
   """
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    iinvoice = get_object_or_404(invoice, id=int(iid))

    for item in iinvoice.item_set.all():
        item.delete()

    iinvoice.delete()

    return HttpResponse("Vymazáno")


@login_required
@csrf_exempt
def rm_item(request, iid):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponse("Chyba oprávnění")

    iitem = get_object_or_404(item, id=int(iid))
    iitem.delete()

    return HttpResponse("Vymazáno")


def next_payment_id(request, HTTP=True):
    max = int("%s0001" % datetime.date.today().strftime("%Y"))
    for x in invoice.objects.all():
        if x.payment_id > max:
            max = x.payment_id
    max += 1
    if HTTP:
        return HttpResponse(max)

    return max

## Django admin

@login_required
def items(request, fid):
    u = request.session.get('switched_user', request.user).parms
    fid = int(fid)
    invoice = get_object_or_404(u.invoice_set, id=fid)

    out = "<table style=\"margin: 20px auto; 20px\">"
    out += "<tr>"
    out += _(u"<th>Co</th>")
    out += _(u"<th>Množství</th>")
    out += _(u"<th>Cena za j.</th>")
    out += _(u"<th>Cena za všechno</th>")
    out += _(u"<th>Akce</th>")
    out += "</tr>"

    for x in invoice.item_set.all():
        out += "<tr>"
        out += "<td>%s</td>" % x.name
        out += "<td>%d</td>" % x.count
        out += "<td>%d,- kč</td>" % x.price_per_one
        out += "<td>%d,- kč</td>" % x.price_per_one * x.count
        out += _(
            u"<td><a href=\"/admin/invoices/item/%d/delete/\" class=\"deletelink\">Smazat</a></td>") % x.id
        out += "</tr>"

    out += "<table>"
    return HttpResponse(out)


@login_required
def stats(request):
    u = request.session.get('switched_user', request.user).parms
    invoices = u.invoice_set.all()

    years = {}

    for x in invoices:
        year = int(x.date_exposure.strftime("%Y"))
        if not year in years:
            years[year] = [0, 0]
        years[year][0] += 1
        years[year][1] += int(x.totalInt())

    out = "<div class=\"module\">"
    out += _(u"<h1>Statistika faktůr</h1>")
    out += "</div>"
    out = "<div class=\"flex\">"
    out += _(u"<h1>Statistika faktůr po jednotlivých letech</h1>")
    out += "<table>"
    out += _(
        u"<tr><th>Rok</th><th>Počet faktůr</th><th>Celková částka</th></tr>")
    for x in years:
        out += "<tr><td>%d</td><td>%d</td><td>%d,- kč</td></tr>" % (
        x, years[x][0], years[x][1])
    out += "</table>"
    out += "</div>"
    return HttpResponse(out)


@login_required
@csrf_exempt
def invoice_get(request, fid):
    fid = int(fid)
    u = request.session.get('switched_user', request.user)

    if u.is_superuser:
        f = invoice.objects.filter(payment_id=fid)
    else:
        f = invoice.objects.filter(client_address=u.parms.address,
                                   payment_id=fid)

    if f:
        pdf = genInvoice(f[0], "/tmp/" + str(f[0].id) + ".pdf")
        pdf.gen()
        fp = open("/tmp/" + str(f[0].id) + ".pdf")
        data = fp.read()
        fp.close()
        os.unlink("/tmp/" + str(f[0].id) + ".pdf")
        r = HttpResponse(data, mimetype="application/pdf")
        r[
        'Content-Disposition'] = "attachment; filename=Faktura-RostiCZ-" + str(
            f[0].payment_id) + ".pdf"
        return r
    return HttpResponse("Chyba při získávání faktury")


@login_required
@csrf_exempt
def send_invoice(request, fid, warning="0"):
    fid = int(fid)
    warning = int(warning)
    u = request.session.get('switched_user', request.user).parms
    #f = u.invoice_set.filter(payment_id=fid)
    f = invoice.objects.filter(payment_id=fid)
    if f:
        f = f[0]
        pdf = genInvoice(f, "/tmp/Faktura-RostiCZ-" + str(fid) + ".pdf")
        pdf.gen()

        if warning:
            tmpl = "send_invoice_warning.txt"
            subject = u'Upozornění na nezaplacení faktury %d za služby %s' % (fid, Site.objects.get_current())
        else:
            tmpl = "send_invoice.txt"
            subject = u'Faktura %d za služby %s' % (fid, Site.objects.get_current())

        email = EmailMessage(subject,
                             render_to_string(tmpl, {
                                 "BA": f.bank_account,
                                 "VS": f.payment_id,
                                 "cash": f.totalInt(),
                                 "expiration": f.date_payback.strftime("%d.%m.%Y"),
                                 'site': Site.objects.get_current(),
                             }), settings.EMAIL_FROM,
            [f.client_address.residency_email, "cx@initd.cz"],
                             headers={'Reply-To': settings.EMAIL_FROM})
        email.attach_file("/tmp/Faktura-RostiCZ-" + str(fid) + ".pdf")
        email.send()

        f.sended = True
        f.save()

        os.unlink("/tmp/Faktura-RostiCZ-" + str(fid) + ".pdf")
        return HttpResponse("Invoice sended")
    return HttpResponse("Invoice not found")
