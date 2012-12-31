from django.forms.models import ModelForm
from wsgiadmin.dns.models import Domain, Record
from wsgiadmin.service.forms import RostiFormHelper


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