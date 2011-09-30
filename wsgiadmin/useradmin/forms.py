# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User as user

class PasswordForm(forms.Form):
    password = forms.CharField(_(u"Password"), widget=forms.PasswordInput)

    def clean_password(self):
        if len(self.cleaned_data["password"]) < 6:
            raise forms.ValidationError(_(u"Password needs at least 6 chars"))

        return self.cleaned_data["password"]


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


class formReg2(forms.Form):
    username = forms.CharField(label=_(u"Username"), max_length=30)
    password1 = forms.CharField(label=_(u"Password"),
                                widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_(u"Password again"),
                                widget=forms.PasswordInput(render_value=False))

    def clean_username(self):
        if user.objects.filter(username=self.cleaned_data["username"]):
            raise forms.ValidationError(_(u"Uživatelské jméno je již obsazeno"))
        return self.cleaned_data["username"]

    def clean_password1(self):
        if not "password1" in self.cleaned_data:
            raise forms.ValidationError(_(u"You have to put your password into both inputs"))
        if len(self.cleaned_data["password1"]) < 6:
            raise forms.ValidationError(_(u"Password needs at least 6 chars"))
        return self.cleaned_data["password1"]

    def clean_password2(self):
        if self.cleaned_data.get("password1") != self.cleaned_data.get("password2"):
            raise forms.ValidationError(_(u"First password isn't equal to second one"))
        if not "password2" in self.cleaned_data:
            raise forms.ValidationError(_(u"You have to fill second password for check"))

        return self.cleaned_data["password2"]


class form_reg_payment(forms.Form):
    pay_method = forms.ChoiceField(
                                   label=_(u"Pay method"),
                                   required=True,
                                   choices=(
                                            ("per_web", _(u"Per application (60Kč/app/month)")),
                                            ("fee", _(u"Constant fee (200 Kč/196 MB RAM)")),
                                   )
                                  )
