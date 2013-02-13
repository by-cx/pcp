import json
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Log(models.Model):
    date = models.DateField(_("Date"), auto_now_add=True)
    content = models.TextField(_("Messages"))

    def get_json(self):
        return json.loads(self.content)

    def __unicode__(self):
        return "Log with id %d" % (self.id)