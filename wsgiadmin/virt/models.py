from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.core.models import Server


class VirtMachine(models.Model):
    created = models.DateTimeField(_("Created date"), auto_now_add=True)
    lastest_update = models.DateTimeField(_("Lastest update"), auto_now=True)
    name = models.CharField(_("Name"), max_length=128)
    user = models.ForeignKey(User)
    server = models.ForeignKey(Server, verbose_name=_("Server"))

    @property
    def ident(self):
        return "vm_%05d" % self.id

    def __unicode__(self):
        return "Virtual machine: %s" % self.name
