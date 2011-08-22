# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User as user
from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _

class ftp(models.Model):
	pub_date	= models.DateField(auto_now=True)
	username	= models.CharField("Přihlašovací jméno",max_length=100,unique=True)
	password	= models.CharField("Heslo",max_length=100)
	uid			= models.IntegerField("UID")
	gid			= models.IntegerField("GID")
	dir			= models.CharField("Homedir",max_length=100)
	
	owner		= models.ForeignKey(user)

	def __repr__(self):
		return "<FTP %s>"%self.email
	def __unicode__(self):
		return "%s"%self.email

class form_ftp(forms.Form):
	u = None

	name		= forms.CharField(label=_(u"Přihlašovací jméno")+" *")
	dir			= forms.ChoiceField(label=_(u"Adresář"))
	password1	= forms.CharField(label=_(u"Heslo poprvé"),widget=forms.PasswordInput(render_value=False))
	password2	= forms.CharField(label=_(u"Heslo pro kontrolu"),widget=forms.PasswordInput(render_value=False))

	def clean_password1(self):
		if not "password1" in self.cleaned_data: raise forms.ValidationError(_(u"Je potřeba vyplnit heslo do obou políček"))
		if len(self.cleaned_data["password1"]) < 6: raise forms.ValidationError(_(u"Heslo musí mít alespoň 6 znaků"))
		return self.cleaned_data["password1"]

	def clean_password2(self):
		if "password1" in self.cleaned_data and "password2" in self.cleaned_data and self.cleaned_data["password1"] != self.cleaned_data["password2"]: raise forms.ValidationError(_(u"První heslo nesouhlasí s druhým"))
		if not "password2" in self.cleaned_data: raise forms.ValidationError(_(u"Je potřeba vyplnit podruhé heslo pro kontrolu"))
		return self.cleaned_data["password2"]
	
	def clean_name(self):
		if list(ftp.objects.filter(username=self.u.username+"_"+self.cleaned_data["name"])):
			raise forms.ValidationError(_(u"Toto uživatelské jméno už je použito"))

		return self.cleaned_data["name"]

class form_ftp_update(forms.Form):
	edit_name = None

	name		= forms.CharField(label=_(u"Přihlašovací jméno")+" *")
	dir			= forms.ChoiceField(label=_(u"Adresář"))
	
	def clean_name(self):
		if len(list(ftp.objects.exclude(username=self.edit_name).filter(username=self.u.username+"_"+self.cleaned_data["name"]))) > 0:
			raise forms.ValidationError(_(u"Toto uživatelské jméno už je použito"))

		return self.cleaned_data["name"]

class form_ftp_passwd(forms.Form):
	password1	= forms.CharField(label=_(u"Heslo poprvé"),widget=forms.PasswordInput(render_value=False))
	password2	= forms.CharField(label=_(u"Heslo pro kontrolu"),widget=forms.PasswordInput(render_value=False))

	def clean_password1(self):
		if not "password1" in self.cleaned_data: raise forms.ValidationError(_(u"Je potřeba vyplnit heslo do obou políček"))
		if len(self.cleaned_data["password1"]) < 6: raise forms.ValidationError(_(u"Heslo musí mít alespoň 6 znaků"))
		return self.cleaned_data["password1"]

	def clean_password2(self):
		if "password1" in self.cleaned_data and "password2" in self.cleaned_data and self.cleaned_data["password1"] != self.cleaned_data["password2"]: raise forms.ValidationError(_(u"První heslo nesouhlasí s druhým"))
		if not "password2" in self.cleaned_data: raise forms.ValidationError(_(u"Je potřeba vyplnit podruhé heslo pro kontrolu"))
		return self.cleaned_data["password2"]
