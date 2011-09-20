# -*- coding: utf-8 -*-

from django import forms
from django.forms.models import ModelForm
from wsgiadmin.emails.models import email, redirect
from django.utils.translation import ugettext_lazy as _

class FormEmail(ModelForm):
    login = forms.CharField(label=_(u"Název"), help_text=_(u"Schánka bude ve formátu název@doména"))
    xdomain = forms.ChoiceField(label=_(u"Doména"), choices=[(11, 22)])
    password1 = forms.CharField(label=_(u"Heslo poprvé"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_(u"Heslo pro kontrolu"), widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = email
        fields = ("login", "xdomain", "password1", "password2")

    def clean_login(self):
        if email.objects.filter(remove=False, domain__name=self.data['xdomain'], login=self.cleaned_data["login"]).count():
            raise forms.ValidationError(_(u"Login už je jednou použit"))

        return self.cleaned_data["login"]

    def clean_password1(self):
        if not "password1" in self.cleaned_data:
            raise forms.ValidationError(_(u"Je potřeba vyplnit heslo do obou políček"))
        if len(self.cleaned_data["password1"]) < 6:
            raise forms.ValidationError(_(u"Heslo musí mít alespoň 6 znaků"))
        return self.cleaned_data["password1"]

    def clean_password2(self):
        if not ("password1" in self.cleaned_data and "password2" in self.cleaned_data):
            raise forms.ValidationError(_(u"Je potřeba vyplnit heslo do obou políček"))

        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            raise forms.ValidationError(_(u"První heslo nesouhlasí s druhým"))

        return self.cleaned_data["password2"]



class FormEmailPassword(ModelForm):
    password1 = forms.CharField(label=_(u"Heslo poprvé"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_(u"Heslo pro kontrolu"), widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = email
        fields = ("password1", "password2")


    def clean_password1(self):
        if not "password1" in self.cleaned_data:
            raise forms.ValidationError(_(u"Je potřeba vyplnit heslo do obou políček"))
        if len(self.cleaned_data["password1"]) < 6:
            raise forms.ValidationError(_(u"Heslo musí mít alespoň 6 znaků"))
        return self.cleaned_data["password1"]

    def clean_password2(self):
        if not ("password1" in self.cleaned_data and "password2" in self.cleaned_data):
            raise forms.ValidationError(_(u"Je potřeba vyplnit heslo do obou políček"))

        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            raise forms.ValidationError(_(u"První heslo nesouhlasí s druhým"))

        return self.cleaned_data["password2"]


class FormLogin(forms.Form):
    username = forms.CharField(label=_(u"Přihlašovací jméno"))
    password = forms.CharField(label=_(u"Heslo"), widget=forms.PasswordInput(render_value=False))


class FormRedirect(ModelForm):
    _domain = forms.ChoiceField(label=_(u"Doména"), choices=[(11, 22)])

    def clean_login(self):
        if email.objects.filter(domain__name=self.data['domain'], login=self.cleaned_data["alias"]).count():
            raise forms.ValidationError(_(u"Alias už je jednou použit"))

        return self.cleaned_data["alias"]

    class Meta:
        model = redirect
        exclude = ("pub_date", "owner", "domain")
        fields = ('alias', '_domain', 'email')

