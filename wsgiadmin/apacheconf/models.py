# -*- coding: utf-8 -*-

from django.contrib.auth.models import User as user
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from os.path import join


class UserSite(models.Model):
    pub_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    type = models.CharField(_(u"Type"), max_length=20,
        choices=[("uwsgi", "uWSGI"), ("modwsgi", "mod_wsgi"), ("php", "PHP"), ("static", "Static")])

    domains = models.CharField(_(u"Domains"), max_length=1024,
        help_text=u"Domény na kterých bude web server naslouchat oddělené mezerou. Například 'rosti.cz www.rosti.cz ' apod. První doména je brána jako hlavní.")

    documentRoot = models.CharField(_(u"DocumentRoot"), max_length=200, blank=True)
    htaccess = models.BooleanField(_(u"htaccess"), default=True)
    indexes = models.BooleanField(_(u"Index adresáře"), default=True)
    allow_ips = models.TextField(_(u"Whitelist"), default="", blank=True)
    deny_ips = models.TextField(_(u"Blacklist"), default="", blank=True, help_text=_("One IP per one line"))

    script = models.CharField(_(u"Script"), max_length=100)
    processes = models.IntegerField(_(u"Počet procesů"), default=1)
    threads = models.IntegerField(_(u"Počet threadů"), default=5)
    virtualenv = models.CharField(_(u"Virtualenv"), default="default", max_length=100)
    static = models.TextField(_(u"Statická data"), default="", blank=True)
    python_path = models.TextField(_(u"Python path"), default="", blank=True)

    extra = models.TextField(_(u"Extra configuration"), blank=True, null=True, default="")

    removed = models.BooleanField(_(u"Smazáno"), default=False) # nezmizí dokud se nezaplatí
    owner = models.ForeignKey(user, verbose_name=_(u'Uživatel'))

    class Meta:
        db_table = 'apacheconf_site'

    @property
    def serverNameSlugged(self):
        return slugify(self.serverName)

    @property
    def pythonPathList(self):
        return [x.strip() for x in self.python_path.split("\n") if x.strip()]

    @property
    def static_list(self):
        statics = []
        for line in self.static.split("\n"):
            try:
                url, target = line.strip().split()
            except ValueError:
                pass
            else:
                target = "%s%s" % (self.owner.parms.home, target)
                statics.append(dict(url=url, dir=target))
        return statics

    @property
    def serverName(self):
        domains = self.domains.split(" ")
        if len(domains):
            return domains[0]
        else:
            return "no-domain"

    @property
    def serverAlias(self):
        domains = self.domains.split(" ")
        if len(domains):
            return " ".join(domains[1:])
        else:
            return ""

    @property
    def pidfile(self):
        return join(self.owner.parms.home, "uwsgi", "%s.pid" % self.serverName)

    @property
    def logfile(self):
        return join(self.owner.parms.home, "uwsgi" , "%s.log" % self.serverName)

    @property
    def socket(self):
        return join(self.owner.parms.home, "uwsgi", "%s.sock" % self.serverName)

    @property
    def virtualenv_path(self):
        return join(self.owner.parms.home, settings.VIRTUALENVS_DIR, "%s" % self.virtualenv)

    @property
    def fastcgiWrapper(self):
        return settings.PCP_SETTINGS["fastcgi_wrapper_dir"] % self.owner

    @property
    def pay(self):
        """
        Vypočítá cenu stránky za den včetně slevy
        """
        if self.owner.parms.fee:
            return 0

        if self.type in ("uwsgi", "modwsgi"):
            return (settings.PAYMENT_WSGI[self.owner.parms.currency] / 30.0) * self.owner.parms.dc()
        elif self.type in ("php",):
            return (settings.PAYMENT_PHP[self.owner.parms.currency] / 30.0) * self.owner.parms.dc()
        else:
            return (settings.PAYMENT_STATIC[self.owner.parms.currency] / 30.0) * self.owner.parms.dc()

    def __repr__(self):
        return "<Web %s>" % self.serverName

    def __unicode__(self):
        return "%s" % (self.serverName)
