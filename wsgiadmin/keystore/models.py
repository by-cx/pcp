from django.db import models
from django.utils.translation import ugettext_lazy as _

class store(models.Model):
    key = models.CharField(_("Key"), max_length=250, unique=True)
    value = models.CharField(_("Value"), max_length=250)
    expire = models.IntegerField(_("Expire"), help_text=_("amount of minutes"), default=0)
    date_read = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_write = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return u"%s: '%s'" % (self.key, self.value)
