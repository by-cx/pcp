from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from gopay4django.models import Payment
from wsgiadmin.clients.models import Address


class RecordExists(Exception): pass


SERVICES = (
    ("old_webs", 'old_webs'), #domain|processes
    ("apps", 'apps'), #domain|processes
    ("modwsgi", 'modwsgi'), #domain|processes
    ("uwsgi", 'uwsgi'), #domain|processes
    ("php", 'php'), #domain
    ("static", 'static'), #domain
    ("pgsql", 'pgsql'), #count
    ("mysql", 'mysql'), #count
    ("ftp", 'ftp'), #count
    ("email", 'email'), #count
    ("fee", 'fee'), #count
    ("correction", 'correction'), #count
)


class Record(models.Model):
    check=True

    date = models.DateField(_("Date"))
    user = models.ForeignKey(User, verbose_name=_("User"))
    service = models.CharField(_("Service"), max_length=128, choices=SERVICES)
    value = models.CharField(_("Value"), max_length=512)
    cost = models.FloatField(_("Cost"), default=0)

    def save(self, force_insert=False, force_update=False, using=None):
        if self.check and Record.objects.filter(date = self.date,
                            user = self.user,
                            service = self.service,
                            value = self.value).count() > 0:
            raise RecordExists()
        super(Record, self).save()

    def __unicode__(self):
        return "%s %s %s for %s" % (self.date, self.user, self.service, self.value)


class Credit(models.Model):
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    date_payed = models.DateTimeField(_("Date paid"), blank=True, null=True)
    user = models.ForeignKey(User, verbose_name=_("User"))
    price = models.FloatField(_("Price"))
    currency = models.CharField(_("Currenty"), max_length=8)
    value = models.FloatField(_("Credits (bonus included)"))
    bonus = models.FloatField(_("Bonus"), default=0)
    address = models.ForeignKey(Address, verbose_name=_("Address"), null=True, blank=True)

    def gopay_payment(self):
        payments = self.gopay_payments()
        if payments:
            return payments[0]
        return None

    def gopay_paid(self):
        for payment in self.gopay_payments():
            if payment.state == "PAID":
                return True
        return False

    def gopay_payments(self):
        return Payment.objects.filter(p4=str(self.id)).order_by("date").reverse()

    def __unicode__(self):
        return "%s += %.2f" % (self.user.username, self.value)


class TransId(models.Model):
    trans_id = models.BigIntegerField(_("Transaction ID"), help_text=_("Transaction ID from bank"))
    credit = models.ForeignKey(Credit)

    def __unicode__(self):
        return self.trans_id


class AssignedDiscountCode(models.Model):
    user = models.ForeignKey(User)


RANGES = (
    ("credits", "Just credits"),
    ("one-time", "One-time % bonus (credit recharge)"),
    ("always", "Always % bonus (each credit recharge)"),
)
class DiscountCodes(models.Model):
    code = models.CharField(_("Code"), max_length=64)
    start_date = models.DateTimeField(_("Start date"))
    end_date = models.DateTimeField(_("End date"))
    description = models.CharField(_("Description"), max_length=256)
    code_type = models.CharField(_("Range"), max_length=256, choices=RANGES)
    value = models.FloatField(_("Discount/Credits"), default=0.0, help_text=_("Amount of credits for credits type, otherwise %"))
