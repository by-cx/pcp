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


class AppParmetersForm(forms.Form):
    helper = RostiFormHelper()

    domains = forms.CharField(
        max_length=512,
        required=False,
        label=_("Domains"),
        help_text=_("Domain is not necessary anymore (in native apps). There is no relation to DNS or Domains menu.")
    )


class AppStaticForm(AppParmetersForm):
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


class AppPHPForm(AppParmetersForm):
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


class AppuWSGIForm(AppParmetersForm):
    def __init__(self, *args, **kwargs):
        super(AppuWSGIForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True
        self.fields["domains"].help_text = "There is no relation to DNS or Domains menu."

    script = forms.CharField(
        label=_("Script"),
        max_length=256,
        widget=forms.TextInput(attrs={"autocomplete": "off"})
    )
    virtualenv = forms.CharField(
        label=_("Virtualenv"),
        max_length=256,
        widget=forms.TextInput(attrs={"autocomplete": "off"})
    )
    python_paths = forms.CharField(
        label=_("Python paths"),
        required=False,
        widget=forms.Textarea,
    )
    static_maps = forms.CharField(
        label=_("Static maps"),
        required=False,
        widget=forms.Textarea,
    )


class AppNativeForm(AppParmetersForm):
    def __init__(self, *args, **kwargs):
        super(AppNativeForm, self).__init__(*args, **kwargs)
        self.fields["domains"] = None

    command = forms.CharField(
        label=_("Commnad"),
        max_length=1024,
    )

class AppProxyForm(AppParmetersForm):
    def __init__(self, *args, **kwargs):
        super(AppProxyForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True
        self.fields["domains"].help_text = "There is no relation to DNS or Domains menu."
