from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.service.forms import PassCheckForm, RegFormHelper
import re

class RegistrationForm(PassCheckForm):
    username = forms.CharField(label=_("Username"), max_length=30, required=True)
    email = forms.EmailField(label=_("E-mail"), max_length=128, required=True)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['email', 'username', 'password1', 'password2']
        self.helper = RegFormHelper()

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data["username"]):
            raise forms.ValidationError(_("This username is already in use"))
        if not re.match("^[0-9a-zA-Z_]*$", self.cleaned_data["username"]):
            raise forms.ValidationError(_("Username has to be in this format: ^[0-9a-zA-Z_]*$"))
        return self.cleaned_data["username"]

class formReg(forms.Form):
    company = forms.CharField(label=_("Company"), max_length=250, required=False)
    first_name = forms.CharField(label=_("First name"), max_length=250)
    last_name = forms.CharField(label=_("Last name"), max_length=250)
    street = forms.CharField(label=_("Street"), max_length=250)
    city = forms.CharField(label=_("City"), max_length=250)
    city_num = forms.CharField(label=_("ZIP"), max_length=6)
    ic = forms.CharField(label=_("IC"), max_length=50, required=False)
    dic = forms.CharField(label=_("DIC"), max_length=50, required=False)
    email = forms.EmailField(label=_("E-mail"), max_length=250)
    phone = forms.CharField(label=_("Phone"), max_length=30)


class formReg2(PassCheckForm):
    username = forms.CharField(label=_("Username"), help_text=_("Will be used as system user"), max_length=30)

    def __init__(self, *args, **kwargs):
        super(formReg2, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['username', 'password1', 'password2']

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data["username"]):
            raise forms.ValidationError(_("Username already exists"))
        if not re.match("^[0-9a-zA-Z_]*$", self.cleaned_data["username"]):
            raise forms.ValidationError(_("Username has to be in this format: ^[0-9a-zA-Z_]*$"))
        return self.cleaned_data["username"]


class SendPwdForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=250, required=True)

    def clean(self):
        user = None
        if 'email' in self.cleaned_data and self.cleaned_data['email']:
            users = User.objects.filter(email=self.cleaned_data['email'])

            if len(users) == 1:
                self.user_object = users[0]
            elif len(users) > 1:
                raise ValidationError(_("Found more than one user with this e-mail address. Please contact technical support."))
            else:
                raise ValidationError(_("Given email doesn't belong to any user"))

        return self.cleaned_data
