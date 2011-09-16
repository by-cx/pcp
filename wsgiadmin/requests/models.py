from django.db import models
from django.contrib.auth.models import User as user
from django.utils.translation import ugettext_lazy as _

ACTIONS = (
    ("run", "Run"),
    ("write", "Write"),
    ("unlink", "Unlink"),
    ("read", "Read"),
)

class Request(models.Model):
    add_date = models.DateTimeField(_("Add date"), auto_now_add=True)
    done_date = models.DateTimeField(_("Done date"), default=None, null=True, blank=True)
    plan_to_date = models.DateTimeField(_("Plan date"), default=None, null=True, blank=True)
    machine = models.CharField(_("Machine"), max_length=100, default="localhost")
    done = models.BooleanField(_("Done"), default=False)
    action = models.CharField(_("Action"), choices=ACTIONS, max_length=20)
    data = models.TextField(_("Data"), blank=True)
    stdout = models.TextField(_("Stdout"), blank=True, null=True)
    stderr = models.TextField(_("Stderr"), blank=True, null=True)
    retcode = models.IntegerField(_("Return code"), default=-1)
    user = models.ForeignKey(user)

    def __unicode__(self):
        return ""
