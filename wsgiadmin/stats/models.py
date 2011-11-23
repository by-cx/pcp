from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class RecordExists(Exception): pass

SERVICES = (
    ("modwsgi", 'modwsgi'), #domain|processes
    ("uwsgi", 'uwsgi'), #domain|processes
    ("php", 'php'), #domain
    ("static", 'static'), #domain
    ("pgsql", 'pgsql'), #count
    ("mysql", 'mysql'), #count
    ("ftp", 'ftp'), #count
    ("email", 'email'), #count
    ("fee", 'fee'), #count
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
    date = models.DateField(_("Date"), auto_now_add=True)
    user = models.ForeignKey(User, verbose_name=_("User"))
    value = models.FloatField(_("Cost"))
    invoice = models.BooleanField(_("Sended to invoice system"), default=False)

    def __unicode__(self):
        return "%s += %.2f" % (self.user.username, self.value)
