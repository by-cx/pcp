# -*- coding: utf-8 -*-

from django.contrib.auth.models import User as user
from django.core.cache import cache
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from wsgiadmin.emails.models import Email
from wsgiadmin.keystore.tools import kget

from wsgiadmin.requests.tools import RawRequest
from wsgiadmin.tools import size_format


class Machine(models.Model):
    name = models.CharField(_(u"Název serveru"), max_length=50)
    domain = models.CharField(_(u"Doménová adresa serveru"), max_length=50)
    ip = models.CharField(_(u"IP adresa serveru"), max_length=50)
    ipv6 = models.CharField(_(u"IPv6 adresa serveru"), max_length=50, blank=True)

    def __repr__(self):
        return "<Machine %s>" % self.name

    def __unicode__(self):
        return "%s" % (self.name)


class Address(models.Model):
    # sídlo
    company = models.CharField(_(u"Jméno společnosti"), max_length=250, blank=True)

    residency_name = models.CharField(_(u"Jméno a příjmení"), max_length=250, blank=True)
    residency_street = models.CharField(_(u"Ulice a č.p."), max_length=250)
    residency_city = models.CharField(_(u"Město"), max_length=250)
    residency_city_num = models.CharField(_(u"PSČ"), max_length=6)
    residency_ic = models.CharField(_(u"IČ"), max_length=50, blank=True)
    residency_dic = models.CharField(_(u"DIČ"), max_length=50, blank=True)
    residency_email = models.CharField(_(u"Email"), max_length=250)
    residency_phone = models.CharField(_(u"Telefon/Mobil"), max_length=30)
    # fakturační
    different = models.BooleanField(_(u"Odlišná od sídla?"), blank=True, default=False)
    invoice_name = models.CharField(_(u"Jméno a příjmení"), max_length=250, blank=True)
    invoice_street = models.CharField(_(u"Ulice a č.p."), max_length=250, blank=True)
    invoice_city = models.CharField(_(u"Město"), max_length=250, blank=True)
    invoice_city_num = models.CharField(_(u"PSČ"), max_length=6, blank=True)
    invoice_email = models.CharField(_(u"Email"), max_length=250, blank=True)
    invoice_phone = models.CharField(_(u"Telefon/Mobil"), max_length=30, blank=True)

    note = models.TextField(_(u"Poznámka"), blank=True)

    def __repr__(self):
        return "<Address %s>" % self.residency_name

    def __unicode__(self):
        if self.company:
            return "%s - %s" % (self.residency_name, self.company)
        else:
            return "%s" % (self.residency_name)

    def getName(self):
        if self.company:
            return "%s - %s" % (self.residency_name, self.company)
        else:
            return "%s" % (self.residency_name)

    def getInvoiceAddress(self):
        addr = []
        if self.company:
            addr.append(self.company)
        if not self.different:
            if not self.company:
                addr.append(self.residency_name)
            addr.append(self.residency_street)
            addr.append("%s %s" % (self.residency_city_num, self.residency_city))
        else:
            if not self.company:
                addr.append(self.invoice_name)
            addr.append(self.invoice_street)
            addr.append("%s %s" % (self.invoice_city_num, self.invoice_city))

        addr.append(" ")
        if self.residency_ic:
            tail = u"Neplátce DPH" if self.id == 1 else ""
            addr.append(u"IČ: %s %s" % (self.residency_ic, tail))
        if self.residency_dic:
            addr.append(u"DIČ: %s" % self.residency_dic)

        return "\n".join(addr)

    def getInvoiceContact(self):
        contact = []
        if not self.different:
            contact.append("Telefon: %" % self.residency_phone)
            contact.append("Email: %s" % self.residency_email)
        else:
            contact.append("Telefon: %s" % self.invoice_phone)
            contact.append("Email: %s" % self.invoice_email)
        return "\n".join(contact)

    class Meta:
        verbose_name = _(u"Adresa")
        verbose_name_plural = _(u"Adresy")



class Parms(models.Model):
    home = models.CharField(_(u"Home"), max_length=100)
    note = models.TextField(_(u"Poznámka"), blank=True)
    uid = models.IntegerField(_(u"UID"))
    gid = models.IntegerField(_(u"GID"))
    discount = models.IntegerField(_(u"Sleva"), default=0) # v procentech
    fee = models.IntegerField(_(u"Paušál"), default=0)
    currency = models.CharField(_(u"Měna"), max_length=20, choices=settings.CURRENCY, default="czk")
    enable = models.BooleanField(_(u"Stav účtu"), default=True)

    #address		= models.ForeignKey("address")
    address = models.OneToOneField(Address)
    web_machine = models.ForeignKey(Machine, related_name="web")
    mail_machine = models.ForeignKey(Machine, related_name="mail")
    mysql_machine = models.ForeignKey(Machine, related_name="mysql")
    pgsql_machine = models.ForeignKey(Machine, related_name="pgsql")

    user = models.OneToOneField(user, verbose_name=_(u'Uživatel'))

    def prefix(self):
        return self.user.username[:3]

    def dc(self):
        """Discount coeficient"""
        if (100 - self.discount) > 0:
            return (100.0 - self.discount) / 100.0
        else:
            return 0.0

    def count_domains(self):
        return self.user.domain_set.count()

    def count_ftps(self):
        return self.user.ftp_set.count()

    def count_pgs(self):
        return self.user.pgsql_set.count()

    def count_mys(self):
        return self.user.mysqldb_set.count()

    def count_sites(self):
        return self.user.usersite_set.count()

    def count_emails(self):
        return Email.objects.filter(domain__in=self.user.domain_set.all(), remove=False).count()

    def home_size(self):
        size = kget("%s:homesize" % self.user.username)
        if size:
            return size_format(int(size))
        else:
            return _("Undetected")

    def pay_for_sites(self, use_cache=True):
        pay = cache.get('user_payment_%s' % self.user_id)
        if pay is None or not use_cache:
            pay = 0.0
            for site in self.user.usersite_set.all():
                pay += site.pay
            cache.set('user_payment_%s' % self.user_id, pay, timeout=3600*24*7)
        return pay

    def pay_total_day(self):
        return self.pay_for_sites()

    def pay_total_month(self):
        return self.pay_for_sites() * 30.0

    def installed(self):
        rr = RawRequest(self.web_machine.ip)
        data = rr.run("cat /etc/passwd |grep ^%s:" % self.user.username)["stdout"].strip()
        return self.user.username in data

    def __repr__(self):
        return "<Config %s>" % self.user.username

    def __unicode__(self):
        return "%s" % (self.user.username)

    class Meta:
        verbose_name = _(u"User")
        verbose_name_plural = _(u"Users")
