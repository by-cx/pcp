from django.conf import settings
from django.forms.models import ModelForm
from django import forms
from wsgiadmin.apps.models import App
from django.utils.translation import ugettext_lazy as _
import re
from wsgiadmin.service.forms import RostiFormHelper


class AppForm(ModelForm):
    helper = RostiFormHelper()

    class Meta:
        model = App
        fields = ("name", "domains")

    def clean_name(self):
        if not re.match("^[0-9a-zA-Z_]*$", self.cleaned_data["name"]):
            raise forms.ValidationError(_("App name has to be in this format: ^[0-9a-zA-Z_]*$"))
        return self.cleaned_data["name"]


class AppParametersForm(forms.Form):
    helper = RostiFormHelper()

    domains = forms.CharField(
        max_length=512,
        required=False,
        label=_("Domains"),
        help_text=_("Domain is not necessary anymore (in native apps). There is no relation to DNS or Domains menu.")
    )


class AppStaticForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppStaticForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True
        self.fields["domains"].help_text = "There is no relation to DNS or Domains menu."

    document_root = forms.CharField(
        max_length=512,
        required=True,
        label=_("Path to your app")
    )
    flag_index = forms.BooleanField(
        label=_("Indexing"),
        help_text=_("Turn on/off indexing of your document root"),
        required=False,
    )


class AppPHPForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppPHPForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True
        self.fields["domains"].help_text = "There is no relation to DNS or Domains menu."

    document_root = forms.CharField(
        max_length=512,
        required=True,
        label=_("Path to your app")
    )
    flag_index = forms.BooleanField(
        label=_("Indexing"),
        help_text=_("Turn on/off indexing of your document root"),
        required=False,
    )


class AppPythonForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppPythonForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True
        self.fields["domains"].help_text = "There is no relation to DNS or Domains menu."

    script = forms.CharField(
        label=_("WSGI Script"),
        max_length=8192,
        widget=forms.Textarea(attrs={"class": "textarea-code"}),
        help_text=_("Write python code, which create WSGI handler of your app.")
    )
    python = forms.ChoiceField(
        label=_("Static maps"),
        required=True,
        choices=[(x, x) for x in settings.PYTHON_INTERPRETERS]
    )
    procs = forms.ChoiceField(
        label=_("Processes"),
        required=True,
        choices=[(x, x) for x in range(1,10)]
    )
    virtualenv = forms.CharField(
        label=_("Virtualenv"),
        max_length=4096,
        widget=forms.Textarea(attrs={"class": "textarea-code"}),
        help_text=_("List of requirements. One package per one line. Like requirements.txt file.")
    )
    static_maps = forms.CharField(
        label=_("Static maps"),
        required=False,
        widget=forms.Textarea(attrs={"class": "textarea-code"}),
        help_text=_("Consider your app as root.")
    )


class AppNativeForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppNativeForm, self).__init__(*args, **kwargs)
        self.fields["domains"] = None

    command = forms.CharField(
        label=_("Commnad"),
        max_length=1024,
    )

class AppProxyForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppProxyForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True
        self.fields["domains"].help_text = "There is no relation to DNS or Domains menu."
