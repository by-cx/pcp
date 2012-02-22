# -*- coding: utf-8 -*-
from datetime import date, timedelta
from constance import config

from django.contrib.auth.models import User as user
from django.core.cache import cache
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from jsonrpc.proxy import ServiceProxy
from wsgiadmin.emails.models import Email, Message
from wsgiadmin.keystore.tools import kget
from wsgiadmin.requests.tools import RawRequest
from wsgiadmin.stats.models import Credit
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

class Parms(models.Model):
    home = models.CharField(_(u"Home"), max_length=100)
    note = models.TextField(_(u"Poznámka"), blank=True)
    uid = models.IntegerField(_(u"UID"))
    gid = models.IntegerField(_(u"GID"))
    discount = models.IntegerField(_(u"Sleva"), default=0) # v procentech
    fee = models.IntegerField(_(u"Paušál"), default=0)
    currency = models.CharField(_(u"Měna"), max_length=20, choices=settings.CURRENCY, default="czk")
    enable = models.BooleanField(_(u"Stav účtu"), default=True)
    low_level_credits = models.CharField(_("Low level of credits"), max_length=30, default="send_email")
    last_notification = models.DateField(_("Last low level notification"), blank=True, null=True)

    #address		= models.ForeignKey("address")
    web_machine = models.ForeignKey(Machine, related_name="web")
    mail_machine = models.ForeignKey(Machine, related_name="mail")
    mysql_machine = models.ForeignKey(Machine, related_name="mysql")
    pgsql_machine = models.ForeignKey(Machine, related_name="pgsql")

    user = models.OneToOneField(user, verbose_name=_(u'Uživatel'))
    # For JSONRPC synchronization
    address_id = models.IntegerField(_("Address ID"), default=0)

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

    @property
    def one_credit_cost(self):
        """Return cost for one credit"""
        #TODO:make currency works
        czk = float(config.credit_currency.split(",")[0])
        return czk

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
        if self.fee:
            return self.fee / 30
        else:
            return self.pay_for_sites()

    def pay_total_month(self):
        if self.fee:
            return self.fee
        else:
            return self.pay_for_sites() * 30.0

    @property
    def credit(self):
        credit = self.user.credit_set.aggregate(Sum("value"))["value__sum"]
        cost = self.user.record_set.aggregate(Sum("cost"))["cost__sum"]
        return (credit if credit else 0) - (cost if cost else 0)

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

    def add_credit(self, value, free=False):
        if settings.JSONRPC_URL:
            items = [{
                "description": config.invoice_desc,
                "count": float(value),
                "price": 1 / float(config.credit_currency.split(",")[0]), #TODO:change it to multicurrency
                "tax": config.tax,
                }]

            proxy = ServiceProxy(settings.JSONRPC_URL)
            #TODO:what to do with exception?
            print proxy.add_invoice(
                settings.JSONRPC_USERNAME,
                settings.JSONRPC_PASSWORD,
                self.address_id,
                items
            )

        bonus = 1.0

        if value >= 1000:
            bonus = config.credit_1000_bonus
        elif value >= 750:
            bonus = config.credit_750_bonus
        elif value >= 500:
            bonus = config.credit_500_bonus
        elif value >= 250:
            bonus = config.credit_250_bonus

        credit = Credit(user=self.user, value=value * bonus, bonus=value * (bonus - 1.0), invoice=free)
        credit.save()

        message = Message.objects.filter(purpose="add_credit")
        if message:
            message[0].send(config.email, {"user": self.user.username, "credit": value, "bonus": value * (bonus - 1.0)})

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
