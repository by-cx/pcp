import json
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Server(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    domain = models.CharField(_("Domain"), max_length=128)
    ip = models.IPAddressField(_("IP address"))
    python = models.BooleanField(_("Python"))
    php = models.BooleanField(_("PHP"))
    mail = models.BooleanField(_("Mail server"))
    virt = models.BooleanField(_("Libvirt"))

    user = models.ForeignKey(User, blank=True, null=True)

    @property
    def libvirt_url(self):
        return "qemu+ssh://root@%s/system" % self.ip

    @property
    def ssh(self):
        return "root@%s" % self.ip

    def __unicode__(self):
        return unicode(self.name)


class Log(models.Model):
    date = models.DateField(_("Date"), auto_now_add=True)
    content = models.TextField(_("Messages"))

    def get_json(self):
        return json.loads(self.content)

    def __unicode__(self):
        return "Log with id %d" % self.id
