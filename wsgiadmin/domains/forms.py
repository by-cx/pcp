import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.domains.models import Domain
from wsgiadmin.service.forms import RostiFormHelper

class FormDomain(forms.models.ModelForm):
    helper = RostiFormHelper()

    class Meta:
        model = Domain
        fields = ["name", "mail", "dns", "ipv4", "ipv6", "enable"]

    def clean_domain(self):
        if not re.search("[a-z0-9\-\.]*\.[a-z]{2,5}", self.cleaned_data["domain"]):
            raise forms.ValidationError(_("Domain is not in valid format"))

        return self.cleaned_data["domain"]

class RegistrationRequestForm(forms.Form):
    domain = forms.CharField(label=_("Domain"))
    mail = forms.BooleanField(label="Manage e-mails records", required=False, initial=False)
    dns = forms.BooleanField(label="Manage DNS records", required=False, initial=False)
    ipv4 = forms.BooleanField(label="Manage IPv4 records in DNS", required=False, initial=False)
    ipv6 = forms.BooleanField(label="Manage IPv6 records ub DNS", required=False, initial=False)

    def clean_domain(self):
        if not re.search("[a-z0-9\-\.]*\.[a-z]{2,5}", self.cleaned_data["domain"]):
            raise forms.ValidationError(_("Domain is not in valid format"))
        domains = [domain.domain_name for domain in Domain.objects.all()]
        if self.cleaned_data["domain"] in domains:
            raise forms.ValidationError(_("This domain is already taken"))

        return self.cleaned_data["domain"]

