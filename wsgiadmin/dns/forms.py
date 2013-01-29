from django import forms
from django.forms.models import ModelForm
from wsgiadmin.dns.models import Domain, Record
from wsgiadmin.service.forms import RostiFormHelper


class DomainUpdateForm(ModelForm):
    helper = RostiFormHelper()

    class Meta:
        model = Domain
        fields = ["rname", "ttl"]


class DomainForm(ModelForm):
    helper = RostiFormHelper()

    class Meta:
        model = Domain
        fields = ["name", "rname", "ttl"]

    def clean_user(self):
        return None


class RecordForm(ModelForm):
    helper = RostiFormHelper()

    class Meta:
        model = Record
        fields = ["name", "record_type", "value", "ttl", "prio"]

    def clean_user(self):
        return None

    def clean_prio(self):
        if self.cleaned_data["record_type"] == "MX" and not self.cleaned_data["prio"]:
            raise forms.ValidationError(_("MX needs prio"))
        return self.cleaned_data["prio"]
