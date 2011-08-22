#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User as user
from django.db import models
from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import re

class site(models.Model):
	pub_date		= models.DateField(auto_now_add=True)
	end_date		= models.DateField(blank=True,null=True)
	serverName		= models.CharField(_(u"ServerName"),max_length=100)
	serverAlias		= models.CharField(_(u"ServerAlias"),max_length=200,blank=True)
	documentRoot	= models.CharField(_(u"DocumentRoot"),max_length=200,blank=True)
	htaccess		= models.BooleanField(_(u"htaccess"),default=True)
	indexes			= models.BooleanField(_(u"Index adresáře"),default=True)
	php				= models.BooleanField(_(u"php"),default=False)
	ipv4			= models.BooleanField(_(u"IPv4"),default=True)
	ipv6			= models.BooleanField(_(u"IPv6"),default=True)
	removed			= models.BooleanField(_(u"Smazáno"),default=False) # nezmizí dokud se nezaplatí

	owner			= models.ForeignKey(user, verbose_name=_('Uživatel'))
	
	def pay(self):
		"""
			Výpočítá cenu stránky za den včetně slevy
		"""
		if self.owner.parms.fee:
			return 0

		try:
			self.wsgi
			wsgi = True
		except:
			wsgi = False
			
		if wsgi:
			return (settings.PAYMENT_WSGI[self.owner.parms.currency]/30.0)*self.owner.parms.dc()
		elif self.php:
			return (settings.PAYMENT_PHP[self.owner.parms.currency]/30.0)*self.owner.parms.dc()
		else:
			return (settings.PAYMENT_STATIC[self.owner.parms.currency]/30.0)*self.owner.parms.dc()
	
	def __repr__(self):
		return "<Stránka %s>"%self.serverName
	def __unicode__(self):
		return "%s"%(self.serverName)

APPENDS = (("None",_(u"Žádný/Jiný")),("Django",_(u"Django")))

class wsgi(models.Model):
	script		= models.CharField(_(u"Script"),max_length=100)
	processes	= models.IntegerField(_(u"Počet procesů"),default=1)
	threads		= models.IntegerField(_(u"Počet threadů"),default=5)
	append		= models.CharField(_(u"Přídavky"),choices=APPENDS,max_length=100) # Přídavky (django, atd.)
	virtualenv	= models.CharField(_(u"Virtualenv"),default="default", max_length=100)
	static		= models.TextField(_(u"Statická data"),default="", blank=True)
	python_path	= models.TextField(_(u"Python path"),default="", blank=True)
	allow_ips	= models.TextField(_(u"Povolené IP adresy"),default="", blank=True)
	site		= models.OneToOneField(site, verbose_name=_('Stránka'))
	uwsgi		= models.BooleanField(_(u"uWSGI"), default=True)

	def pidfile(self):
		return self.site.owner.parms.home+"/uwsgi/%s.pid" % self.site.serverName

	def logfile(self):
		return self.site.owner.parms.home+"/uwsgi/%s.log" % self.site.serverName

	def socket(self):
		return self.site.owner.parms.home+"/uwsgi/%s.sock" % self.site.serverName

	def virtualenv_path(self):
		return self.site.owner.parms.home+"/virtualenvs/%s" % self.virtualenv

	def __repr__(self):
		return "<wsgi %s>"%self.script
	def __unicode__(self):
		return "%s"%(self.script)

class alias(models.Model):
	name		= models.CharField(_(u"Alias"),max_length=100)
	directory	= models.CharField(_(u"Adresář"),max_length=100)
	indexes		= models.BooleanField(_(u"Index adresáře"),default=True)
	site		= models.ForeignKey(site)

	def __unicode__(self):
		return "%s"%(self.name)

class custom(models.Model):
	conf		= models.TextField(_(u"Specialitky"))
	site		= models.ForeignKey(site)

	def __unicode__(self):
		return "Custom %s"%(self.id)

class formStatic(forms.Form):
	serverName		= forms.CharField(label=_(u"Hlavní doména (ServerName)"),help_text=_(u"<br />Hlavní doména, např. example.com"))
	serverAlias		= forms.CharField(label=_(u"Další doména (ServerAlias)"),help_text=_(u"<br />Další domény včetně subdomén oddělené mezerami<br />např.: *.example.com example2.com www.example2.com"),required=False)
	documentRoot	= forms.ChoiceField(label=_(u"Adresář"))

class formWsgi(forms.Form):
	serverName		= forms.CharField(label=_(u"Hlavní doména (ServerName) *"),help_text=_(u"<br />Hlavní doména, např. example.com"))
	serverAlias		= forms.CharField(label=_(u"Další doména (ServerAlias)"),help_text=_(u"<br />Další domény včetně subdomén oddělené mezerami<br />např.: *.example.com example2.com www.example2.com"),required=False)
	static			= forms.CharField(label=_(u"Adresáře se statickými soubory"), widget=forms.Textarea, help_text=_(u"<br /><strong>~/&lt;zadaná_cesta&gt;</strong> - Jeden řádek, jeden adresář. Formát <strong>/url/ /cesta/k/mediím/</strong> - Odělovačem je mezera. Chybné řádky budou při generování konfigurace ignorovány."), required=False)
	python_path		= forms.CharField(label=_(u"Python path"), widget=forms.Textarea, help_text=_(u"<br /><strong>~/&lt;zadaná_cesta&gt;</strong> - Jeden řádek, jeden adresář. Formát <strong>/tady/je/moje/aplikace</strong>. Váš domovský adresář bude automaticky doplněn. uWSGI ignoruje nastavení PYTHON_PATH přes sys.path."), required=False)
	virtualenv		= forms.ChoiceField(label=_(u"Virtualenv *"),choices=(("default","default"),), initial="default", help_text=_(u"<br />Pythoní virtuální prostředí. Najdete je ve '<strong>~/virtualenvs/&lt;zadaná_hodnota&gt;</strong>'. Můžete si si vytvořit vlastní přes SSH."), required=True)
	script			= forms.ChoiceField(label=_(u"WSGI skript *"))
	allow_ips		= forms.CharField(label=_(u"Povolené IPv4 adresy"), widget=forms.Textarea, help_text=_(u"<br />Jedna IP adresa na jeden řádek. Pokud je pole prázdné, fungují všechny."), required=False)

	def clean_allow_ips(self):
		ips = [x.strip() for x in self.cleaned_data["allow_ips"].split("\n") if x]

		for ip in ips:
			if not re.match("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",ip):
				raise forms.ValidationError(_(u"Jedna nebo více zadaných IP adres má špatný tvar"))

		return self.cleaned_data["allow_ips"]

	def clean_virtualenv(self):
		if "." in self.cleaned_data["virtualenv"] or "~" in self.cleaned_data["virtualenv"] or "/" in self.cleaned_data["virtualenv"]: raise forms.ValidationError(_(u"Virtualenv nesmí obsahovat znaky ./~"))
		return self.cleaned_data["virtualenv"]
	
	def clean_static(self):
		if ".." in self.cleaned_data["static"] or "~" in self.cleaned_data["static"]: raise forms.ValidationError(_(u"Toto pole nesmí obsahovat nesmí obsahovat .. a ~"))
		return self.cleaned_data["static"]
