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

class App(models.Model):
    date = models.DateField(_("Date"), auto_now_add=True)
    app_type = models.CharField(_("Type"), max_length=20, choices=SITE_TYPE_CHOICES, blank=True, null=True)
    name = models.CharField(_("Name"), max_length=256, help_text=_("Name of your application"))
    domains = models.CharField(_("Domains"), max_length=512, blank=True, null=True, help_text=_("Domain is not necessary anymore. There is no relation to DNS or Domains menu."))
    parameters_data = models.TextField(_("Parameters"), blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)

    def parameters_get(self):
        return json.loads(self.parameters_data if self.parameters_data else "{}")
    def parameters_set(self, value):
        self.parameters_data = json.dumps(value, indent=4)
    parameters = property(parameters_get, parameters_set)

    @property
    def main_domain(self):
        domains = self.domains_list
        if domains:
            return domains[0]
        else:
            return None

    @property
    def domains_list(self):
        return [x.strip() for x in self.domains.split(" ")]

    @property
    def price(self):
        return 0.0

    def __repr__(self):
        return "<App %s>" % self.name

    def __unicode__(self):
        return "%s" % self.name
