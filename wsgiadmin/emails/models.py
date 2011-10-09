from django.db import models
from django.utils.translation import ugettext_lazy as _
from constance import config

class Email(models.Model):
    pub_date = models.DateField(auto_now=True)
    login = models.CharField(_("Login"), max_length=100)
    domain = models.ForeignKey("domains.Domain")
    password = models.CharField(_("Heslo"), max_length=100)
    uid = models.IntegerField(_("UID"), default=config.email_uid)
    gid = models.IntegerField(_("GID"), default=config.email_gid)
    homedir = models.CharField(_("Homedir"), max_length=100, default="/var/mail")
    remove = models.BooleanField(_("Remove"), default=False)

    def address(self):
        return "%s@%s" % (self.login, self.domain.name)

    def __unicode__(self):
        return "%s@%s" % (self.login, self.domain.name)


class EmailRedirect(models.Model):
    pub_date = models.DateField(auto_now=True)
    alias = models.CharField(_("Alias (origin)"), max_length=100, blank=True, help_text=_("&lt;alias&gt;@&lt;chosen domain&gt;"))
    domain = models.ForeignKey("domains.Domain")
    email = models.CharField(_("E-mail (destination)"), max_length=250, help_text=_("Email address to redirect mails to"))

    class Meta:
        db_table = 'emails_redirect'
        unique_together = ( ('alias', 'domain', 'email'), )

    def __unicode__(self):
        return "%s to %s" % (self.alias, self.email)
