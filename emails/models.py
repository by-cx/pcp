# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User as user
from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _

import domains.models as domains

class email(models.Model):
	pub_date	= models.DateField(auto_now=True)
	login		= models.CharField(_(u"Login"),max_length=100)
	domain		= models.ForeignKey("domains.domain")
	password	= models.CharField(_(u"Heslo"),max_length=100)
	uid			= models.IntegerField(_(u"UID"),default="117")
	gid			= models.IntegerField(_(u"GID"),default="118")
	homedir		= models.CharField(_(u"Homedir"),max_length=100,default="/var/mail")
	remove		= models.BooleanField(_(u"Smazat?"),default=False)
	
	def owner(self):
		return self.domain.owner()

	def address(self):
		return "%s@%s"%(self.login,self.domain.name)

	def __unicode__(self):
		return "%s@%s"%(self.login,self.domain.name)

class formEmail(ModelForm):
	login		= forms.CharField(label=_(u"Název"),help_text=_(u"Schánka bude ve formátu název@doména"))
	xdomain		= forms.ChoiceField(label=_(u"Doména"),choices=[(11,22)])
	password1	= forms.CharField(label=_(u"Heslo poprvé"),widget=forms.PasswordInput(render_value=False))
	password2	= forms.CharField(label=_(u"Heslo pro kontrolu"),widget=forms.PasswordInput(render_value=False))

	def clean_login(self):
		d = domains.domain.objects.filter(name=self.data["xdomain"])[0]
		#d = self.data["domain"][0]
		if len(email.objects.filter(remove=False,domain=d,login=self.cleaned_data["login"])) == 0:
			return self.cleaned_data["login"]
		else:
			raise forms.ValidationError(_(u"Login už je jednou použit"))

	def clean_password1(self):
		if not "password1" in self.cleaned_data: raise forms.ValidationError(_(u"Je potřeba vyplnit heslo do obou políček"))
		if len(self.cleaned_data["password1"]) < 6: raise forms.ValidationError(_(u"Heslo musí mít alespoň 6 znaků"))
		return self.cleaned_data["password1"]

	def clean_password2(self):
		if "password1" in self.cleaned_data and "password2" in self.cleaned_data and self.cleaned_data["password1"] != self.cleaned_data["password2"]: raise forms.ValidationError(_(u"První heslo nesouhlasí s druhým"))
		if not "password2" in self.cleaned_data: raise forms.ValidationError(_(u"Je potřeba vyplnit podruhé heslo pro kontrolu"))
		return self.cleaned_data["password2"]

	class Meta:
		model = email
		exclude = ("pub_date","password","uid","gid","homedir","remove","domain")

class formEmailPassword(ModelForm):
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

	class Meta:
		model = email
		exclude = ("login","domain","pub_date","password","uid","gid","homedir","remove")


class formLogin(forms.Form):
	username		= forms.CharField(label=_(u"Přihlašovací jméno"))
	password	= forms.CharField(label=_(u"Heslo"),widget=forms.PasswordInput(render_value=False))

class redirect(models.Model):
	pub_date	= models.DateField(auto_now=True)
	alias		= models.CharField(_(u"Alias (odsud)"),max_length=100,blank=True, help_text="&lt;zadaný alias&gt;@&lt;vybraná doména&gt;")
	domain		= models.ForeignKey("domains.domain")
	email		= models.CharField(_(u"E-mail (sem)"),max_length=250, help_text="Celý e-mail na který se mají e-maily přeposílat")

	def __unicode__(self):
		return "%s to %s"%(self.alias,self.email)


class formRedirect(ModelForm):
	_domain		= forms.ChoiceField(label=_(u"Doména"),choices=[(11,22)])
	
	def clean_login(self):
		d = domains.domain.objects.filter(name=self.data["domain"])[0]
		if len(email.objects.filter(domain=d,login=self.cleaned_data["alias"])) == 0:
			return self.cleaned_data["alias"]
		else:
			raise forms.ValidationError(_(u"Alias už je jednou použit"))

	class Meta:
		model = redirect
		exclude = ("pub_date","owner","domain")
		fields = ('alias', '_domain', 'email')

