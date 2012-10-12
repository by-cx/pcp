import json

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

SITE_TYPE_CHOICES = [
    ("uwsgi", "uWSGI"),
    ("modwsgi", "mod_wsgi"),
    ("php", "PHP"),
    ("static", "Static"),
    ("nodejs", "Node.js"),
    ("native", "Native"),
]

class App(models.Model):
    date = models.DateField(auto_now_add=True)
    type = models.CharField(_("Type"), max_length=20, choices=SITE_TYPE_CHOICES)
    name = models.CharField(_("Name"), max_length=256, help_text=_("Name of your application"))
    domains = models.CharField(_("Domains"), max_length=512, blank=True, null=True, help_text=_("Domain is not necessary anymore. There is no relation to DNS or Domains menu."))
    parameters_data = models.TextField(_("Parameters"), blank=True, null=True)
    user = models.ForeignKey(User)

    def parameters_get(self):
        return json.loads(self.parameters_data)
    def parameters_set(self, value):
        self.parameters_data = json.dumps(value)
    parameters = property(parameters_get, parameters_set)

    def __repr__(self):
        return "<App %s>" % self.name

    def __unicode__(self):
        return "%s" % self.name
