import re

from django import forms
from django.utils.translation import ugettext_lazy as _

class RegistrationRequestForm(forms.Form):
    domain = forms.CharField(label=_("Domain"))
    ipv4 = forms.BooleanField(label="Manage IPv4 records", required=False, initial=True)
    ipv6 = forms.BooleanField(label="Manage IPv6 records", required=False, initial=True)

    def clean_domain(self):
        if not re.search("[a-z0-9\-\.]*\.[a-z]{2,5}", self.cleaned_data["domain"]):
            raise forms.ValidationError(_("Domain is not in valid format"))

        return self.cleaned_data["domain"]
