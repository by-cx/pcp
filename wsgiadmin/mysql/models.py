# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User as user

from django.utils.translation import ugettext_lazy as _

from mysql.tools import *

class mysqldb(models.Model):
	dbname  = models.CharField(_(u"Název MySQL databáze"), max_length=50)
	owner   = models.ForeignKey(user, verbose_name=_(u"Uživatel"))

	def __unicode__(self):
		return "%s (%s)"%(self.dbname, self.owner)

class form_db(forms.Form):
	database = forms.CharField(label=_(u"Název databáze"), help_text="Název databáze (i vytvořené uživatelské jméno) bude doplněn o prefix ve tvaru <i>prefix_názevdatabáze</i>, kde prefix jsou první tři znaky vašeho uživatelského jména.")
	password = forms.CharField(label=_(u"Heslo k databázi"), widget=forms.PasswordInput)
	
	def clean_database(self):
		if len(self.cleaned_data["database"]) > 8: raise forms.ValidationError(_(u"Název databáze může mít maximálně 8 znaků"))
		else: return self.cleaned_data["database"]

	def clean_password(self):
		if len(self.cleaned_data["password"]) < 6: raise forms.ValidationError(_(u"Heslo musí 6 a více znaků"))
		else: return self.cleaned_data["password"]
