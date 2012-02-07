from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

CRON_CHOICES = [
    ("5m", _("every 5 minutes")),
    ("10m", _("every 10 minutes")),
    ("15m", _("every 15 minutes")),
    ("20m", _("every 20 minutes")),
    ("30m", _("every 30 minutes")),
    ("1h", _("every hour")),
    ("2h", _("every 2 hours")),
    ("3h", _("every 3 hours")),
    ("6h", _("every 6 hours")),
    ("12h", _("every 12 hours")),
    ("1d", _("every day")),
    ("2d", _("every 2 days")),
    ("3d", _("every 3 days")),
    ("4d", _("every 4 days")),
    ("5d", _("every 5 days")),
    ("6d", _("every 6 days")),
    ("7d", _("every 7 days")),
]

TIMES = {
    "5m": "*/5 * * * *",
    "10m": "*/10 * * * *",
    "15m": "*/15 * * * *",
    "20m": "*/20 * * * *",
    "30m": "*/30 * * * *",
    "1h": "0 * * * *",
    "2h": "0 */2 * * *",
    "3h": "0 */3 * * *",
    "6h": "0 */6 * * *",
    "12h": "0 */12 * * *",
    "1d": "0 0 * * *",
    "2d": "0 0 */2 * *",
    "3d": "0 0 */3 * *",
    "4d": "0 0 */4 * *",
    "5d": "0 0 */5 * *",
    "6d": "0 0 */6 * *",
    "7d": "0 0 */7 * *"
}


class Cron(models.Model):
    time = models.CharField(_("Time period"), max_length=32, choices=CRON_CHOICES, default="1h")
    script = models.CharField(_("Path to script"), max_length=512, unique=True, help_text=_("Whole path, including your home directory. Script has to have execute permissions"))

    owner = models.ForeignKey(User, verbose_name=_("User"))

    @property
    def display_time(self):
        return [y for x, y in CRON_CHOICES if x == self.time][0]

    @property
    def cron_config(self):
        return TIMES[self.time]

    def __unicode__(self):
        return "%s (%s)" % (self.script, self.time)