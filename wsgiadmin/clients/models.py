# -*- coding: utf-8 -*-
from datetime import date, timedelta
from constance import config

from django.contrib.auth.models import User as user
from django.core.cache import cache
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from wsgiadmin.emails.models import Email


class Machine(models.Model):
    name = models.CharField(_(u"Název serveru"), max_length=50)
    domain = models.CharField(_(u"Doménová adresa serveru"), max_length=50)
    ip = models.CharField(_(u"IP adresa serveru"), max_length=50)
    ipv6 = models.CharField(_(u"IPv6 adresa serveru"), max_length=50, blank=True)

    def __repr__(self):
        return "<Machine %s>" % self.name

    def __unicode__(self):
        return "%s" % (self.name)


class Parms(models.Model):
    home = models.CharField(_(u"Home"), max_length=100)
    note = models.TextField(_(u"Poznámka"), blank=True)
    uid = models.IntegerField(_(u"UID"))
    gid = models.IntegerField(_(u"GID"))
    discount = models.IntegerField(_(u"Sleva"), default=0) # v procentech
    fee = models.IntegerField(_(u"Paušál"), default=0, help_text=_("Credits per 30 days"))
    currency = models.CharField(_(u"Měna"), max_length=20, choices=settings.CURRENCY, default="CZK")
    enable = models.BooleanField(_(u"Stav účtu"), default=True)
    guard_enable = models.BooleanField(_(u"Kontrola automatem"), default=True)
    low_level_credits = models.CharField(_("Low level of credits"), max_length=30, default="send_email")
    last_notification = models.DateField(_("Last low level notification"), blank=True, null=True)
    installed = models.BooleanField(_("Installed"), default=False)

    #address		= models.ForeignKey("address")
    web_machine = models.ForeignKey(Machine, related_name="web")
    mail_machine = models.ForeignKey(Machine, related_name="mail")
    mysql_machine = models.ForeignKey(Machine, related_name="mysql")
    pgsql_machine = models.ForeignKey(Machine, related_name="pgsql")

    user = models.OneToOneField(user, verbose_name=_(u'Uživatel'))

    def prefix(self):
        return self.user.username.replace(".", "")[:3]

    def dc(self):
        """Discount coeficient"""
        if (100 - self.discount) > 0:
            return (100.0 - self.discount) / 100.0
        else:
            return 0.0

    @property
    def count_domains(self):
        return self.user.domain_set.count()

    @property
    def count_ftps(self):
        return self.user.ftp_set.count()

    @property
    def count_pgs(self):
        return self.user.pgsql_set.count()

    @property
    def count_mys(self):
        return self.user.mysqldb_set.count()

    @property
    def count_apps(self):
        return self.user.app_set.count()

    @property
    def count_sites(self):
        return self.user.usersite_set.count()

    @property
    def count_emails(self):
        return Email.objects.filter(domain__in=self.user.domain_set.all(), remove=False).count()

    @property
    def one_credit_cost(self):
        return float(config.credit_quotient)

    def pay_for_sites(self, use_cache=True):
        pay = cache.get('user_payment_%s' % self.user_id)
        if pay is None or not use_cache:
            pay = 0.0
            for site in self.user.usersite_set.all():
                pay += site.pay
            cache.set('user_payment_%s' % self.user_id, pay, timeout=3600*24*7)
        return pay

    def pay_for_apps(self):
        return sum(app.price for app in self.user.app_set.all())


    def pay_total_day(self):
        if self.fee:
            return self.fee / 30
        else:
            return self.pay_for_sites() + self.pay_for_apps()

    def pay_total_month(self):
        if self.fee:
            return self.fee
        else:
            return (self.pay_for_sites() + self.pay_for_apps()) * 30.0

    @property
    def credit(self):
        credit = self.user.credit_set.exclude(date_payed=None).aggregate(Sum("value"))["value__sum"]
        cost = self.user.record_set.aggregate(Sum("cost"))["cost__sum"]
        return (credit if credit else 0) - (cost if cost else 0)

    @property
    def credit_cached(self):
        if not cache.get('credit_%s' % self.user.username):
            result = cache.get('credit_%s' % self.user.username, self.credit, 21600)
        else:
            result = cache.get('credit_%s' % self.user.username)
        return result

    @property
    def var_symbol(self):
        return "%d%.4d" % (config.var_symbol_prefix, self.user.id)

    @property
    def days_left(self):
        credit = self.credit
        pay_per_day = self.pay_total_day()
        if pay_per_day > 0:
            days = credit / pay_per_day
            if days > 0:
                return days
            else:
                return 0
        else:
            return 0

    @property
    def credit_until(self):
        credit = self.credit
        pay_per_day = self.pay_total_day()
        if not pay_per_day:
            return False
        days = int(credit/pay_per_day)
        if days > 0:
            return date.today() + timedelta(days)
        return False

    def delete(self, using=None):
        for x in self.user.record_set.all():
            x.delete()
        for x in self.user.credit_set.all():
            x.delete()
        return super(Parms, self).delete(using)

    def __repr__(self):
        return "<Config %s>" % self.user.username

    def __unicode__(self):
        return "%s" % (self.user.username)

    class Meta:
        verbose_name = _(u"User")
        verbose_name_plural = _(u"Users")


class Address(models.Model):
    default = models.BooleanField(_("Default address"), default=True)
    company = models.CharField(_("Company"), max_length=100, blank=True)
    first_name = models.CharField(_("First name"), max_length=100)
    last_name = models.CharField(_("Last name"), max_length=100)
    street = models.CharField(_("Address"), max_length=100)
    city = models.CharField(_("City"), max_length=100)
    zip = models.CharField(_("ZIP"), max_length=12)

    phone = models.CharField(_("Phone"), max_length=30)
    email = models.EmailField(_("E-mail"))

    company_number = models.CharField(_("Company identification number"), max_length=50, blank=True)
    vat_number = models.CharField(_("VAT registration number"), max_length=50, blank=True)

    user = models.ForeignKey(user, verbose_name=_(u'User'), blank=True, null=True)
    removed = models.BooleanField(_("Removed"), default=False)

    @property
    def address(self):
        if self.company:
            return "%s, %s, %s, %s" % (self.company, self.street, self.zip, self.city)
        else:
            return "%s %s, %s, %s, %s" % (self.first_name, self.last_name, self.street, self.zip, self.city)

    @property
    def name(self):
        if self.company: return "%s - %s %s" % (self.company, self.first_name, self.last_name)
        else: return "%s %s" % (self.first_name, self.last_name)

    def __unicode__(self):
        return self.name