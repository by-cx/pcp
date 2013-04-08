from django.conf import settings
from django.forms.models import ModelForm
from django import forms
from wsgiadmin.apps.models import App, Db
from django.utils.translation import ugettext_lazy as _
import re
from wsgiadmin.core.utils import get_virt_servers
from wsgiadmin.service.forms import RostiFormHelper
from wsgiadmin.virt.models import VirtMachine


class VirtForm(forms.ModelForm):
    helper = RostiFormHelper()

    def __init__(self, *args, **kwargs):
        super(VirtForm, self).__init__(*args, **kwargs)
        self.fields["server"].queryset = get_virt_servers(self.app_type)

    class Meta:
        fields = ("name", )
        model = VirtMachine

