from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Ftp(models.Model):
    pub_date = models.DateField(auto_now=True)
    username = models.CharField(_("Login"), max_length=100, unique=True)
    password = models.CharField(_("Password"), max_length=100)
    uid = models.IntegerField(_("UID"))
    gid = models.IntegerField(_("GID"))
    dir = models.CharField(_("Home directory"), max_length=100)
    enable = models.BooleanField(_("Enable"), default=True)

    owner = models.ForeignKey(User)

    def __repr__(self):
        return "<FTP %s>" % self.dir

    def __unicode__(self):
        return "%s" % self.dir


