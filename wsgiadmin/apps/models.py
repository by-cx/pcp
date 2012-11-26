import json

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

SITE_TYPE_CHOICES = [
    ("uwsgi", "uWSGI"),
    ("php", "PHP"),
    ("static", "Static"),
    ("nodejs", "Node.js"),
    ("native", "Native"),
]


class Server(models.Model):
    hostname = models.CharField(_("Hostname/address"), max_length=256, help_text=_("it has to match with ssh config"))
    ip = models.CharField(_("IP"), max_length=128, blank=True, null=True)
    comment = models.TextField(_("Comment"), blank=True, null=True)

    def __unicode__(self):
        if self.comment:
            return "%s (%s)" % (self.hostname, self.comment)
        else:
            return self.hostname


class App(models.Model):
    date = models.DateField(_("Date"), auto_now_add=True)
    disabled = models.BooleanField(_("Installed"), default=False)
    installed = models.BooleanField(_("Installed"), default=False)
    app_type = models.CharField(_("Type"), max_length=20, choices=SITE_TYPE_CHOICES, blank=True, null=True)
    name = models.CharField(_("Name"), max_length=256, help_text=_("Name of your application"))
    domains = models.CharField(_("Domains"), max_length=512, blank=True, null=True)
    parameters_data = models.TextField(_("Parameters"), blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    server = models.ForeignKey(Server, verbose_name=_("Server"))

    def parameters_get(self):
        return json.loads(self.parameters_data if self.parameters_data else "{}")

    def parameters_set(self, value):
        self.parameters_data = json.dumps(value, indent=4)

    parameters = property(parameters_get, parameters_set)

    def format_parameters(self):
        parms = {}
        for k, v in self.parameters.items():
            if "\n" in v:
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
    def price(self):
        return 0.0

    def __repr__(self):
        return "<App %s>" % self.name

    def __unicode__(self):
        return "%s" % self.name


class Log(models.Model):
    date = models.DateField(_("Date"), auto_now_add=True)
    app = models.ForeignKey(App, verbose_name=_("App"))
    content = models.TextField(_("Messages"))

    def __unicode__(self):
        return "Log with id %d for %s app" % (self.id, self.app_id)


class Db(models.Model):
    date = models.DateField(_("Date"), auto_now_add=True)
    db_type = models.CharField(_("DB engine"), max_length=32, choices=(("mysql", "MySQL"), ("pgsql", "PgSQL")))
    name = models.CharField(_("Name"), max_length=32)
    password = models.CharField(_("Password"), max_length=256)
    comment = models.TextField(_("Comment"), blank=True, null=True)
    app = models.ForeignKey(App, verbose_name=_("App"))

    def __unicode__(self):
        return "%s db for %s app" % (self.name, self.app_id)