from django.forms.models import ModelForm
from django.forms import ValidationError
from wsgiadmin.apps.models import App
from django.utils.translation import ugettext_lazy as _
import re

class FormApp(ModelForm):
    class Meta:
        model = App
        fields = ("name", "type", "domains")

    def clean_name(self):
        if not re.match("^[0-9a-zA-Z_]*$", self.cleaned_data["name"]):
            raise ValidationError(_("App name has to be in this format: ^[0-9a-zA-Z_]*$"))

        return self.cleaned_data["name"]