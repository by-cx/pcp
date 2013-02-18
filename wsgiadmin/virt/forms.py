from django.conf import settings
from django.forms.models import ModelForm
from django import forms
from wsgiadmin.apps.models import App, Db
from django.utils.translation import ugettext_lazy as _
import re
from wsgiadmin.service.forms import RostiFormHelper


class VirtForm(forms.ModelForm):
    helper = RostiFormHelper()

    class Meta:
        fields = ("name", )

