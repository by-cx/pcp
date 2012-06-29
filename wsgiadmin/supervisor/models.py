from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class Program(models.Model):
    name = models.CharField(_("Program name"), max_length=128, help_text=_("Unique name"), unique=True)
    command = models.CharField(_("Command"), max_length=512, )
    environment = models.CharField(_("Environment"), max_length=256, )
    directory = models.CharField(_("Directory"), max_length=512, )
    autostart = models.BooleanField(_("Autostart"), default=True)
    autorestart = models.BooleanField(_("Autorestart"), default=True)

    user = models.ForeignKey(User)