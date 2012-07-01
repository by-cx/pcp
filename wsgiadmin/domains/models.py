from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Domain(models.Model):
    name = models.CharField(_("Domain name"), max_length=100, unique=True)
    pub_date = models.DateField(auto_now=True)
    serial = models.IntegerField(_("Domain's serial no."), default=0)
    dns = models.BooleanField(_("Manage DNS records"), default=True)
    mail = models.BooleanField(_("Manage email"), default=True)
    ipv4 = models.BooleanField(_("IPv4 records"), default=True)
    ipv6 = models.BooleanField(_("IPv6 records"), default=True)
    parent = models.ForeignKey("self", verbose_name=_("Depends on"), null=True, blank=True, related_name="subdomains")
    owner = models.ForeignKey(User)

    @property
    def domain_name(self):
        if self.parent:
            return "%s.%s" % (self.name, self.parent.name)
        else:
            return self.name

    def delete(self, using=None):
        for x in self.parent_set.all():
            x.delete()
        super(Domain, self).delete(using)

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

