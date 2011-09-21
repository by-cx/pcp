# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from wsgiadmin.apacheconf.models import UserSite

from wsgiadmin.bills.models import bill, service
from wsgiadmin.invoices.models import invoice, item
from wsgiadmin.invoices.views import next_payment_id

from django.contrib.auth.models import User as user

from wsgiadmin.keystore.tools import *

import datetime, logging


def aggregate(u, processed=False):
    """Vygeneruje souhrné informace o platbách jednoho uživatele

       processed - vybrat všechny (True) nebo nezpracované do faktur (False)

       vrací [celková částka, začátek, konec, seznam položek]
                    0            1       2          3
   """

    if not processed:
        data = list(u.bill_set.filter(processed=processed))
    else:
        data = list(u.bill_set.all())

    infos = {}

    for line in data:
        if line.info not in infos:
            infos[line.info] = 0.0

    for info in infos:
        total = 0.0
        min_date = None
        max_date = None
        items = []
        for line in data:
            if line.info == info:
                total += line.price
                if min_date is None or min_date > line.pub_date:
                    min_date = line.pub_date
                if max_date is None or max_date < line.pub_date:
                    max_date = line.pub_date
                items.append(line)
        infos[info] = [total, min_date, max_date, items]

    return infos


def bill_services(now=datetime.date.today()):
    """Vytvoření plateb pro doplňkové služby za každý den"""
    day = now.day
    month = now.month
    year = now.year

    for s in service.objects.all():
        if s.one_day_price() == 0:
            continue
        if kget("bill:service:%d:%d:%d:%d" % (
        s.id, day, month, year)) != "processed":
            b = bill()
            b.price = s.one_day_price() * s.user.parms.dc()
            b.info = s.info
            b.user = s.user
            b.save()

            logging.info(
                "Vygenerována platba za službu %s pro uživatele %s v hodnotě %.2f" % (
                s.info, s.user.username, s.one_day_price() * s.user.parms.dc()))

            kset("bill:service:%d:%d:%d:%d" % (s.id, day, month, year),
                 "processed", 20160)
    logging.info("Počítám služby za dnešek")


def bill_hosting(now=datetime.date.today()):
    """Vytvoření plateb pro hostingové služby"""
    day = now.day
    month = now.month
    year = now.year

    for u in user.objects.all():
        #Fee process
        if u.parms.fee:
            if day == u.date_joined.day and kget(
                "bill:hosting:fee:%d:%d:%d:%d" % (
                u.id, day, month, year)) != "processed":
                b = bill()
                b.price = u.parms.fee
                b.info = "Hosting na serveru %s" % Site.objects.get_current()
                b.user = u
                b.currency = u.parms.currency
                b.save()

                kset("bill:hosting:fee:%d:%d:%d:%d" % (u.id, day, month, year),
                     "processed", 20160)

    sites = UserSite.objects.all()
    for s in sites:
        #per page fee process
        if s.pay == 0:
            continue

        if kget("bill:hosting:%d:%d:%d:%d" % (
        s.id, day, month, year)) == "processed":
            continue

        b = bill()
        b.price = s.pay
        b.info = "Hosting na doméně %s (ID:%d)" % (s.server_name, s.id)
        b.user = s.owner
        b.currency = s.owner.parms.currency
        b.save()

        logging.info(
            "Vygenerována platba za hosting doménu %s pro uživatele %s v hodnotě %.2f" % (
            s.server_name, s.owner.username, s.pay))

        kset("bill:hosting:%d:%d:%d:%d" % (s.id, day, month, year), "processed",
             20160)

    # delete sites marked as removed
    UserSite.objects.filter(removed=True).delete()

    logging.info(u"Počítám hosting za dnešek")


def create_invoices(process=True, min=300):
    if process: logging.info("Generuji faktury")
    total = 0.0

    for u in user.objects.all():
        total1 = 0.0
        data = aggregate(u)

        if data:
            utotal = 0
            for line in data:
                utotal += data[line][0]

            if utotal < min:
                continue

            inv = invoice()
            inv.payment_id = int(next_payment_id(None, False))
            inv.client_address = u.parms.address
            inv.currency = u.parms.currency
            inv.sended = False
            inv.payed = False
            inv.sign = True
            inv.byhand = False
            if process: inv.save()

            for line in data:
                itm = item()
                if data[line][1].date() == data[line][2].date():
                    itm.name = "%s - od %s do %s" % (
                    line, data[line][1].strftime("%d.%m.%Y"),
                    data[line][2].strftime("%d.%m.%Y"))
                else:
                    itm.name = "%s - od %s do %s" % (
                    line, data[line][1].strftime("%d.%m.%Y"),
                    data[line][2].strftime("%d.%m.%Y"))
                itm.count = 1
                itm.price_per_one = int(data[line][0])
                total += int(data[line][0])
                total1 += int(data[line][0])
                itm.invoice = inv
                if process: itm.save()

                for bi in data[line][3]:
                    bi.processed = True
                    if process: bi.save()

            if process:
                logging.info(
                    "Vygenerována faktura %d pro uživatele %s v hodnotě %s" % (
                    inv.payment_id, u.username, inv.total()))
            else:
                print "Faktura pro uživatele %s v hodnotě %s kč" % (
                u.username, total1)
    print "Celkově: %f kč" % total
