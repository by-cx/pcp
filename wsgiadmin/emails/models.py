# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class email(models.Model):
    pub_date = models.DateField(auto_now=True)
    login = models.CharField(_(u"Login"), max_length=100)
    domain = models.ForeignKey("domains.Domain")
    password = models.CharField(_(u"Heslo"), max_length=100)
    uid = models.IntegerField(_(u"UID"), default="117")
    gid = models.IntegerField(_(u"GID"), default="118")
    homedir = models.CharField(_(u"Homedir"), max_length=100, default="/var/mail")
    remove = models.BooleanField(_(u"Smazat?"), default=False)

    def owner(self):
        return self.domain.owner

    def address(self):
        return "%s@%s" % (self.login, self.domain.name)

    def __unicode__(self):
        return "%s@%s" % (self.login, self.domain.name)


class redirect(models.Model):
    pub_date = models.DateField(auto_now=True)
    alias = models.CharField(_(u"Alias (odsud)"), max_length=100, blank=True, help_text="&lt;zadaný alias&gt;@&lt;vybraná doména&gt;")
    domain = models.ForeignKey("domains.Domain")
    email = models.CharField(_(u"E-mail (sem)"), max_length=250, help_text=u"Celý e-mail na který se mají e-maily přeposílat")

    def __unicode__(self):
        return "%s to %s" % (self.alias, self.email)
