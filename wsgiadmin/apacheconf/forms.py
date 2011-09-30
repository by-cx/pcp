# -*- coding: utf-8 -*-

import re

from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.apacheconf.models import UserSite
from wsgiadmin.apacheconf.tools import get_user_wsgis, get_user_venvs


class FormStatic(forms.Form):
    domains = forms.CharField(label=_("Domains"), help_text=_(u"<br />Domains separed by space, for example 'rosti.cz www.rosti.cz ' etc. First domain is main."))
    documentRoot = forms.ChoiceField(label=_("Directory"))


class FormWsgi(ModelForm):

    class Meta:
        model = UserSite
        fields = ('domains', 'static', 'python_path', 'virtualenv', 'script', 'allow_ips')
        widgets = {
            'static': forms.Textarea,
            'python_path': forms.Textarea,
            'allow_ips': forms.Textarea,
            'virtualenv': forms.Select,
            'script': forms.Select,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super(FormWsgi, self).__init__(*args, **kwargs)

        self.fields['domains'].help_text = _(u"<br />Domains separed by space, for example 'rosti.cz www.rosti.cz ' etc. First domain is main.")
        self.fields['static'].help_text = _(u"<br />Format <strong>/url/ /path/to/media/</strong>, separated by space.<br /><ul><li>/path/to/media/ is path without your home directory</li><li>one directory per one line</li><li>wrong lines will be ignored</li></ul>.")
        self.fields['python_path'].help_text=_(u"<br /><strong>~/&lt;your_path&gt;</strong> - One directory per line. Format <strong>/there/is/my/app</strong>. Path is without your home directory")
        self.fields['virtualenv'].help_text= _(u"<br />Python virtual environment. You can find yours in '<strong>~/virtualenvs/&lt;selected_virtualenv&gt;</strong>'. Be free create new one.")
        self.fields['allow_ips'].help_text = help_text=_(u"<br />One IP per line. If it is blank, no limitation will be applied.")

        wsgis = get_user_wsgis(self.user)
        wsgis_choices = [("", _("Not selected"))] + [(x, x) for x in wsgis]

        virtualenvs = get_user_venvs(self.user)
        virtualenvs_choices = [("", _("Not selected"))] + [(one, one) for one in virtualenvs]

        self.fields["virtualenv"].widget.choices = virtualenvs_choices
        self.fields['script'].widget.choices = wsgis_choices
        


    def clean_allow_ips(self):
        ips = [x.strip() for x in self.cleaned_data["allow_ips"].split("\n") if x.strip()]

        for ip in ips:
            if not re.match("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip):
                raise forms.ValidationError(_(u"One or more IP addresses are in wrong format"))

        return self.cleaned_data["allow_ips"]

    def clean_virtualenv(self):
        if "." in self.cleaned_data["virtualenv"] or \
           "~" in self.cleaned_data["virtualenv"] or \
           "/" in self.cleaned_data["virtualenv"]:
            raise forms.ValidationError(_(u"Virtualenv hasn't to contain chars ./~"))
        return self.cleaned_data["virtualenv"]

    def clean_static(self):
        if ".." in self.cleaned_data["static"] or \
           "~" in self.cleaned_data["static"]:
            raise forms.ValidationError(_(u"This field hasn't to contain .. and ~"))
        return self.cleaned_data["static"]
