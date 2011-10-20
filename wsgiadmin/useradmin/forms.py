from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.service.forms import PassCheckForm
from django.conf import settings

class formReg(forms.Form):
    company = forms.CharField(label=_("Company"), max_length=250, required=False)
    name = forms.CharField(label=_("Name"), max_length=250)
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
        return self.cleaned_data["username"]


class PaymentRegForm(forms.Form):
    pay_method = forms.ChoiceField(label=_("Pay method"), required=True, choices=settings.PAYMENT_CHOICES)


class SendPwdForm(forms.Form):

    email = forms.EmailField(label=_("E-mail"), max_length=250, required=False)
    username = forms.CharField(label=_("Username"), max_length=250, required=False)


    def clean(self):
        if not 'email' in self.cleaned_data and not 'username' in self.cleaned_data:
            raise ValidationError(_("Fill at least one input"))

        if 'email' in self.cleaned_data and self.cleaned_data['email']:
            try:
                user = User.objects.get(email=self.cleaned_data['email'])
            except User.DoesNotExist:
                raise ValidationError(_("Given email doesn't belong to any user"))

        if 'username' in self.cleaned_data and self.cleaned_data['username']:
            try:
                user = User.objects.get(username=self.cleaned_data['username'])
            except User.DoesNotExist:
                raise ValidationError(_("Given username doesn't exists"))

        self.user_object = user
        return self.cleaned_data
