from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
import re

from wsgiadmin.emails.models import Email, EmailRedirect, Domain
from wsgiadmin.service.forms import PassCheckModelForm, RostiFormHelper


class FormEmail(PassCheckModelForm):
    login = forms.CharField(label=_("Name"), help_text=_("Mailbox in name@domain format"))
    xdomain = forms.ChoiceField(label=_("Domain"), choices=[(11, 22)])

    class Meta:
        model = Email
        fields = ("login", "xdomain", "password1", "password2")

    def clean_login(self):
        if Email.objects.filter(domain__name=self.data['xdomain'], login=self.cleaned_data["login"]).count():
            raise forms.ValidationError(_("Given username already exists"))
        if not re.match("^[0-9a-zA-Z_\.]*$", self.cleaned_data["login"]):
            raise forms.ValidationError(_("Login has to be in this format: ^[0-9a-zA-Z_\.]*$"))

        return self.cleaned_data["login"]


class FormLogin(forms.Form):
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))


class FormRedirect(ModelForm):
    _domain = forms.ChoiceField(label=_("Domain"), choices=[(11, 22)])

    class Meta:
        model = EmailRedirect
        exclude = ("pub_date", "owner", "domain")
        fields = ('alias', '_domain', 'email')


    def clean_login(self):
        if Email.objects.filter(domain__name=self.data['domain'], login=self.cleaned_data["alias"]).count():
            raise forms.ValidationError(_("Given alias already exists"))

        return self.cleaned_data["alias"]


class DomainForm(forms.ModelForm):
    helper = RostiFormHelper()

    class Meta:
        model = Domain
        fields = ("name", )

    def clean_name(self):
        if not re.match("^[0-9a-zA-Z\.]*$", self.cleaned_data["name"]):
            raise forms.ValidationError(_("Domain name has to be in this format: ^[0-9a-zA-Z\.]*$"))

    def clean_user(self):
        return None