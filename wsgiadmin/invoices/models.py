# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
import datetime

from django.conf import settings

from wsgiadmin.clients.models import *

PAYTYPE = ((u"převodem", _(u"převodem")), (u"hotově", _(u"hotově")))

def getMe():
    return Address.objects.get(residency_ic="74943421")

#return address.objects.get(id=4)

class invoice(models.Model):
    bank = models.CharField(_(u"Banka"), max_length=70, default=settings.BANK)
    bank_account = models.CharField(_(u"Účet"), max_length=70, default=settings.BANK_ACCOUNT)
    date_exposure = models.DateField(default=datetime.date.today())
    date_payback = models.DateField(default=datetime.date.today() + datetime.timedelta(18))
    payment_id = models.IntegerField(default=0, unique=True)
    paytype = models.CharField(_(u"Typ platby"), max_length=20, choices=PAYTYPE, default=PAYTYPE[0][0])
    currency = models.CharField(_("Měna"), max_length=20, choices=settings.CURRENCY)
    client_address = models.ForeignKey(Address, related_name="Client")
    sended = models.BooleanField(_(u"Odesláno?"), default=False)
    payed = models.BooleanField(_(u"Zaplaceno?"), default=False)
    sign = models.BooleanField(_(u"Vložit podpis"), default=True)
    #ALTER TABLE invoices_invoice ADD COLUMN byhand boolean DEFAULT 't';
    byhand = models.BooleanField(_(u"Vytvořena ručně"), default=True)

    def __repr__(self):
        return "<Invoice %s>" % self.payment_id

    def __unicode__(self):
        return "%s" % self.payment_id

    def total(self):
        #FIXME
        t = 0
        for x in self.item_set.all():
            t += x.price_per_one * x.count
        return u"%d,- kč" % t

    def totalInt(self):
        #FIXME
        t = 0
        for x in self.item_set.all():
            t += x.price_per_one * x.count
        return t

    def name(self):
        return self.client_address.residency_name

    def downloadLink(self):
        return _(u"<a href=\"%s\">Stáhnout</a>") % reverse("wsgiadmin.invoices.views.invoice_get", args=[self.payment_id])
    downloadLink.short_description = 'Stáhnout PDF'
    downloadLink.allow_tags = True

    def date_exposure_format(self):
        return self.date_exposure.strftime("%d.%m.%Y")

    def date_payback_format(self):
        return self.date_payback.strftime("%d.%m.%Y")

    class Meta:
        verbose_name = _(u"Faktura")
        verbose_name_plural = _(u"Faktury")


class item(models.Model):
    name = models.CharField(_(u"Co"), max_length=250)
    count = models.IntegerField(_(u"Počet kusů"), default=1)
    price_per_one = models.IntegerField(_(u"Cena za kus"), default=0)

    invoice = models.ForeignKey("invoice")

    def total(self):
        return self.count * self.price_per_one

    def __repr__(self):
        return "<Item %s>" % self.name

    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = _(u"Položka")
        verbose_name_plural = _(u"Položky")

