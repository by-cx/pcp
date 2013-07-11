import json

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.core.models import Server

SITE_TYPE_CHOICES = [
    ("uwsgi", "uWSGI"),
    ("php", "PHP"),
    ("static", "Static"),
    ("nodejs", "Node.js"),
    ("native", "Native"),
]

class App(models.Model):
    date = models.DateField(_("Date"), auto_now_add=True)
    disabled = models.BooleanField(_("Disabled"), default=False)
    installed = models.BooleanField(_("Installed"), default=False)
    app_type = models.CharField(_("Type"), max_length=20, choices=SITE_TYPE_CHOICES, blank=True, null=True)
    name = models.CharField(_("Name"), max_length=256, help_text=_("Name of your application"))
    domains = models.CharField(_("Domains"), max_length=512, blank=False, null=False)
    parameters_data = models.TextField(_("Parameters"), blank=True, null=True)
    addons_data = models.TextField(_("Addons"), blank=True, null=True, help_text=_("Extra stuff: databases for example"))
    ssl_cert = models.TextField(_("SSL cert"), blank=True, null=True, help_text=_("Service cert + CA cert"))
    ssl_key = models.TextField(_("SSL key"), blank=True, null=True, help_text=_("Key without password"))
    user = models.ForeignKey(User, blank=True, null=True)
    core_server = models.ForeignKey(Server, verbose_name=_("Server"), null=True) #TODO: not entirly clean
    db_server = models.ForeignKey(Server, verbose_name=_("Server for database"), null=True, blank=True, related_name="app_db_set")

    def parameters_get(self):
        return json.loads(self.parameters_data if self.parameters_data else "{}")

    def parameters_set(self, value):
        self.parameters_data = json.dumps(value, indent=4)

    parameters = property(parameters_get, parameters_set)


    def addons_get(self):
        return json.loads(self.addons_data if self.addons_data else "{}")

    def addons_set(self, value):
        self.addons_data = json.dumps(value, indent=4)

    addons = property(addons_get, addons_set)

    def format_parameters(self):
        parms = {}
        for k, v in self.parameters.items():
            if type(v) == bool:
                parms[k] = _("Yes") if v else _("No")
            elif "\n" in v:
                parms[k] = "<pre>%s</pre>" % v.replace("\n", "<br>").replace(" ", "&nbsp;")
            else:
                parms[k] = v.replace(" ", "&nbsp;")
        return parms

    @property
    def main_domain(self):
        domains = self.domains_list
        return domains[0] if domains else None

    @property
    def domains_list(self):
        return [x.strip() for x in self.domains.split()]

    @property
    def misc_domains_list(self):
        domains = [x.strip() for x in self.domains.split()]
        return domains[1:] if len(domains) > 1 else []

    @property
    def price(self):
        if self.disabled:
            return 0.0
        if self.user.parms.fee > 0:
            return 0.0
        if self.app_type == "static":
            return (5.0/30.0) * self.user.parms.dc()
        return (25.0/30.0) * self.user.parms.dc()

    def __repr__(self):
        return "<App %s>" % self.name

    def __unicode__(self):
        return "%s" % self.name


class Db(models.Model):
    date = models.DateField(_("Date"), auto_now_add=True)
    db_type = models.CharField(_("DB engine"), max_length=32, choices=(("mysql", "MySQL"), ("pgsql", "PgSQL")))
    password = models.CharField(_("Password"), max_length=256)
    pg_postgis = models.BooleanField(_("PostGIS support"), default=False, help_text=_("Just for PostgreSQL"))
    comment = models.TextField(_("Comment"), blank=True, null=True)
    app = models.ForeignKey(App, verbose_name=_("App"))

    @property
    def name(self):
        return "%s_%.5d" % (self.db_type[0:2], self.id)

    def __unicode__(self):
        return self.name #"%s db for %s app" % (self.name, self.app_id)


class TaskLog(models.Model):
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    app = models.ForeignKey(App)
    msg = models.CharField(_("Message"), max_length=512)
    complete = models.BooleanField(_("Complete"), default=False)
    error = models.BooleanField(_("Error"), default=False)
    backend_msg = models.CharField(_("Message from backend"), max_length=512, blank=True, null=True)

    def __unicode__(self):
        return u"%s - %s" % (self.app.name, self.msg)