# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User as user

class PasswordForm(forms.Form):
    password = forms.CharField(_(u"Heslo"), widget=forms.PasswordInput)

    def clean_password(self):
        if len(self.cleaned_data["password"]) < 6:
            raise forms.ValidationError(_(u"Heslo musí 6 a více znaků"))

        return self.cleaned_data["password"]


class formReg(forms.Form):
    company = forms.CharField(label=_(u"Název firmy"), max_length=250,
                              required=False)
    name = forms.CharField(label=_(u"Jméno a příjmení *"), max_length=250)
    street = forms.CharField(label=_(u"Uliče a č.p. *"), max_length=250)
    city = forms.CharField(label=_(u"Město *"), max_length=250)
    city_num = forms.CharField(label=_(u"PSČ *"), max_length=6)
    ic = forms.CharField(label=_(u"IČ"), max_length=50, required=False)
    dic = forms.CharField(label=_(u"DIČ"), max_length=50, required=False)
    email = forms.CharField(label=_(u"Email *"), max_length=250)
    phone = forms.CharField(label=_(u"Telefon/Mobil *"), max_length=30)


class formReg2(forms.Form):
    username = forms.CharField(label=_(u"Uživatelské jméno *"), max_length=30)
    password1 = forms.CharField(label=_(u"Heslo poprvé *"),
                                widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_(u"Heslo pro kontrolu *"),
                                widget=forms.PasswordInput(render_value=False))

    def clean_username(self):
        if user.objects.filter(username=self.cleaned_data["username"]):
            raise forms.ValidationError(_(u"Uživatelské jméno je již obsazeno"))
        return self.cleaned_data["username"]

    def clean_password1(self):
        if not "password1" in self.cleaned_data:
            raise forms.ValidationError(_(u"Je potřeba vyplnit heslo do obou políček"))
        if len(self.cleaned_data["password1"]) < 6:
            raise forms.ValidationError(_(u"Heslo musí mít alespoň 6 znaků"))
        return self.cleaned_data["password1"]

    def clean_password2(self):
        if self.cleaned_data.get("password1") != self.cleaned_data.get("password2"):
            raise forms.ValidationError(_(u"První heslo nesouhlasí s druhým"))
        if not "password2" in self.cleaned_data:
            raise forms.ValidationError(_(u"Je potřeba vyplnit podruhé heslo pro kontrolu"))

        return self.cleaned_data["password2"]


class form_reg_payment(forms.Form):
    pay_method = forms.ChoiceField(label=_(u""), required=True, choices=(
        ("per_web", u"Za každou aplikaci (60Kč/app/měsíc)"),
        ("fee", u"Paušální poplatek (200 Kč/196 MB RAM)"))
    )
