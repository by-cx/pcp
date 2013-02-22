from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.core.models import Server


class VirtMachine(models.Model):
    created = models.DateTimeField(_("Created date"), auto_now_add=True)
    lastest_update = models.DateTimeField(_("Lastest update"), auto_now=True)
    name = models.CharField(_("Name"), max_length=128)
    own_ident = models.CharField(_("Ownident"), max_length=128, blank=True, null=True)
    user = models.ForeignKey(User)
    server = models.ForeignKey(Server, verbose_name=_("Server"))

    @property
    def ident(self):
        if self.own_ident:
            return self.own_ident
        return "vm_%05d" % self.id

    def __unicode__(self):
        return "Virtual machine: %s" % self.name


class VirtVariant(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    cpus = models.IntegerField("Number of CPUs")
    memory = models.IntegerField(_("Memory"), help_text=_("in MB unit"))
    disk_size = models.IntegerField(_("Disk size"), help_text=_("in GB unit"))
    credits = models.FloatField(_("Credits per day"))

    def __unicode__(self):
        return self.name