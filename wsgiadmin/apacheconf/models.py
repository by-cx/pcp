from constance import config

from django.contrib.auth.models import User as user
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from os.path import join

SITE_TYPE_CHOICES = [
    ("uwsgi", "uWSGI"),
    ("modwsgi", "mod_wsgi"),
    ("php", "PHP"),
    ("static", "Static")
]


class UserSite(models.Model):
    pub_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    type = models.CharField(_("Type"), max_length=20, choices=SITE_TYPE_CHOICES)

    domains = models.CharField(_("Domains"), max_length=1024,
        help_text=_("VirtualHost domains, space separated; ie. 'rosti.cz www.rosti.cz '; First domain is taken as primary"))

    document_root = models.CharField(_("DocumentRoot"), max_length=200, blank=True)
    htaccess = models.BooleanField(_(".htaccess"), default=True)
    indexes = models.BooleanField(_("Allow directory index"), default=True)
    allow_ips = models.TextField(_("Whitelist"), blank=True)
    deny_ips = models.TextField(_("Blacklist"), blank=True, help_text=_("One IP per one line"))

    script = models.CharField(_("Script"), max_length=100, blank=True)
    processes = models.IntegerField(_("No. of proccesses"), default=1, blank=True)
    threads = models.IntegerField(_("No. of threads"), default=5, blank=True)
    virtualenv = models.CharField(_("Virtualenv"), default="default", max_length=100, blank=True)
    static = models.TextField(_("Static data path"), blank=True)
    python_path = models.TextField(_("Python path"), blank=True)

    extra = models.TextField(_("Extra configuration"), blank=True, null=True)
    ssl_crt = models.CharField(_("SSL certificate filename"), blank=True, null=True, max_length=256)
    ssl_key = models.CharField(_("SSL key filename"), blank=True, null=True, max_length=256)
    ssl_mode = models.CharField(_("SSL mode"), choices=(("none", "None"), ("sslonly", "SSL Only"), ("both", "Both")), max_length=20, default="none")

    removed = models.BooleanField(_("Removed"), default=False) # nezmizi dokud se nezaplati
    owner = models.ForeignKey(user, verbose_name=_('Owner'))

    class Meta:
        db_table = 'apacheconf_site'

    @property
    def python_paths(self):
        return [x.strip() for x in self.python_path.split("\n") if x.strip()]

    @property
    def static_list(self):
        statics = []
        for line in self.static.split("\n"):
            try:
                url, target = line.strip().split()
                target = target.strip("/") + "/"
            except ValueError:
                pass
            else:
                if not target.startswith(self.owner.parms.home.rstrip('/')):
                    target = join(self.owner.parms.home, target)
                statics.append(dict(url=url, dir=target))
        return statics

    @property
    def server_name(self):
        domains = self.domains.split()
        if len(domains):
            return domains[0]
        else:
            return "no-domain"

    @property
    def serverAlias(self):
        domains = self.domains.split()
        if domains:
            return " ".join(domains[1:])
        else:
            return ""

    @property
    def pidfile(self):
        return join(self.owner.parms.home, "uwsgi", "%s.pid" % self.server_name)

    @property
    def logfile(self):
        return join(self.owner.parms.home, "uwsgi" , "%s.log" % self.server_name)

    @property
    def socket(self):
        return join(self.owner.parms.home, "uwsgi", "%s.sock" % self.server_name)

    @property
    def virtualenv_path(self):
        return join(self.owner.parms.home, settings.VIRTUALENVS_DIR, "%s" % self.virtualenv)

    @property
    def fastcgiWrapper(self):
        return config.fastcgi_wrapper_dir % self.owner

    @property
    def pay(self):#AttributeError:
        """
        Credits per day
        """
        if self.owner.parms.fee:
            return 0

        if self.type in ("uwsgi", "modwsgi"):
            return (float(self.processes) * config.credit_wsgi_proc + config.credit_wsgi) * self.owner.parms.dc()
        elif self.type in ("php",):
            return config.credit_php * self.owner.parms.dc()
        else:
            return config.credit_static * self.owner.parms.dc()

    def __repr__(self):
        return "<Web %s>" % self.server_name

    def __unicode__(self):
        return "%s" % self.server_name
