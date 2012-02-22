from constance import config
from django.core.mail.message import EmailMessage
from django.db import models
from django.template.context import Context
from django.utils.translation import ugettext_lazy as _
from django.template.base import Template

CHOICES = (
    ("reg", _("Registration")),
    ("approved_reg", _("Approved registration")),
    ("low_credit", _("Low credit notification")),
    ("autobuy_credit", _("Autobuy credit")),
    ("add_credit", _("Credit notification - admin")),
)

class Message(models.Model):
    purpose = models.CharField(_("Purpose"), max_length=20, choices=CHOICES)
    lang = models.CharField(_("Language"), max_length=5, blank=True, null=True)
    subject = models.CharField(_("Subject"), max_length=100)
    body = models.TextField(_("Body"))

    def __unicode__(self):
        return self.subject

    def send(self, email, context={}):
        template = Template(self.body)
        message = EmailMessage(self.subject,
                            template.render(Context(context)),
                            from_email=config.email,
                            to=[email],
                            bcc=[config.email],
                            headers={'Reply-To': config.email})
        message.send()


class Email(models.Model):
    pub_date = models.DateField(auto_now=True)
    login = models.CharField(_("Login"), max_length=100)
    domain = models.ForeignKey("domains.Domain")
    password = models.CharField(_("Heslo"), max_length=100)
    uid = models.IntegerField(_("UID"))
    gid = models.IntegerField(_("GID"))
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
