# -*- coding: utf-8 -*-

from django import forms
from django.forms import models
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.db.models import MySQLDB, PGSQL

class MysqlForm(models.ModelForm):

    class Meta:
        model = MySQLDB
        fields = ( 'dbname', 'password',)

    #database = forms.CharField(label=_(u"Název databáze"), help_text="Název databáze (i vytvořené uživatelské jméno) bude doplněn o prefix ve tvaru <i>prefix_názevdatabáze</i>, kde prefix jsou první tři znaky vašeho uživatelského jména.")
    password = forms.CharField(label=_(u"Heslo k databázi"), widget=forms.PasswordInput)

    def clean_database(self):
        if len(self.cleaned_data["database"]) > 8:
            raise forms.ValidationError(_(u"Název databáze může mít maximálně 8 znaků"))

        return self.cleaned_data["database"]

    def clean_password(self):
        if len(self.cleaned_data["password"]) < 6:
            raise forms.ValidationError(_(u"Heslo musí 6 a více znaků"))
        return self.cleaned_data["password"]


class PgsqlForm(MysqlForm):

    class Meta:
        model = PGSQL
        fields = ( 'dbname', 'password',)
