from django import forms
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User as user
from wsgiadmin.service.forms import PassCheckForm
from django.conf import settings

class formReg(forms.Form):
    company = forms.CharField(label=_(u"Company"), max_length=250,
                              required=False)
    name = forms.CharField(label=_(u"Name"), max_length=250)
    street = forms.CharField(label=_(u"Street"), max_length=250)
    city = forms.CharField(label=_(u"City"), max_length=250)
    city_num = forms.CharField(label=_(u"ZIP"), max_length=6)
    ic = forms.CharField(label=_(u"IC"), max_length=50, required=False)
    dic = forms.CharField(label=_(u"DIC"), max_length=50, required=False)
    email = forms.CharField(label=_(u"E-mail"), max_length=250)
    phone = forms.CharField(label=_(u"Phone"), max_length=30)


class formReg2(PassCheckForm):
    username = forms.CharField(label=_("Username"), help_text=_("Will be used as system user"), max_length=30)

    def __init__(self, *args, **kwargs):
        super(formReg2, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['username', 'password1', 'password2']

    def clean_username(self):
        if user.objects.filter(username=self.cleaned_data["username"]):
            raise forms.ValidationError(_("Username already exists"))
        return self.cleaned_data["username"]


class PaymentRegForm(forms.Form):
    pay_method = forms.ChoiceField(label=_("Pay method"), required=True, choices=settings.PAYMENT_CHOICES)
