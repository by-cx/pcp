from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

CHOICES = [ (".cz", ".cz"), (".eu", ".eu"), (".cz.cc", ".cz.cc"),
            (".co.cz", ".co.cz"), (".com", ".com"),
            (".org", ".org"), (".net", ".net"), (".biz", ".biz"),
            (".info", ".info"), (".name", ".name")]
YEARS =   [ ("1", "1 rok"), ("2", "2 roky"), ("3", "3 roky") ]

class Domain(models.Model):
    name = models.CharField(_("Domain name"), max_length=100, unique=True)
    pub_date = models.DateField(auto_now=True)
    serial = models.IntegerField(_("Domain's serial no."), default=0)
    dns = models.BooleanField(_("Manage DNS records"), default=True)
    mail = models.BooleanField(_("Manage email"), default=True)
    ipv4 = models.BooleanField(_("IPv4 records"), default=True)
    ipv6 = models.BooleanField(_("IPv6 records"), default=True)
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return "%s" % self.name


class RegistrationRequest(models.Model):
    name = models.CharField(_("Domain name"), max_length=100, unique=True)
    pub_date = models.DateField(auto_now=True)
    kind = models.CharField(_("Registration/transfer"), max_length=20,
        choices=(("registration", _("Registration of new domain")), ("transfer", _("Trasnfer existing domain"))))
    ip = models.CharField(_("Origin IP address of request"), max_length=50)
    hostname = models.CharField(_("Origin hostname of request"), max_length=50)
    passwd = models.CharField(_("Transfer password"), max_length=100, blank=True)
    years = models.IntegerField(_("No. of years"), default=1)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return "%s" % self.name

