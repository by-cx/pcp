import json
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

CAPABILITIES = [(x, x) for x in ("python", "php", "mail", "static", "load_balancer", "ns_primary", "ns_secondary", "native")]

class Capability(models.Model):
    name = models.CharField(_("Capability"), max_length=32, choices=CAPABILITIES)
    #config = models.TextField(_("Config for capability"), help_text=_("Use docs for details"))

    def __unicode__(self):
        return unicode(self.__str__())

    def __str__(self):
        return self.name


class Server(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    domain = models.CharField(_("Domain"), max_length=128)
    ip = models.IPAddressField(_("IP address"), default="127.0.0.1")
    ssh_port = models.IntegerField(_("SSH Port"), default=22)
    capabilities = models.ManyToManyField(Capability, verbose_name=_("Capabilities"))

    user = models.ForeignKey(User, blank=True, null=True)

    @property
    def capabilities_str(self):
        return ", ".join([x.name for x in self.capabilities.all()])

    @property
    def libvirt_url(self):
        return "qemu+ssh://%s/system" % self.ssh

    @property
    def ssh(self):
        return "root@%s:%d" % (self.ip, self.ssh_port)

    @property
    def ssh_cmd(self):
        return "ssh root@%s -p %d" % (self.ip, self.ssh_port)

    def __unicode__(self):
        return unicode(self.name)


class Log(models.Model):
    date = models.DateField(_("Date"), auto_now_add=True)
    content = models.TextField(_("Messages"))

    def get_json(self):
        return json.loads(self.content)

    def __unicode__(self):
        return "Log with id %d" % self.id
