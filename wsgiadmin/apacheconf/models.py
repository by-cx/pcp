#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User as user
from django.db import models
from django.forms import ModelForm
from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import re

class Site(models.Model):
	pub_date		= models.DateField(auto_now_add=True)
	end_date		= models.DateField(blank=True,null=True)
	type            = models.CharField(_(u"Type"), max_length=20, choices=[("uwsgi","uWSGI"), ("modwsgi","mod_wsgi"), ("php","PHP"), ("static","Static")])

	domains         = models.CharField(_(u"Domains"), max_length=1024, help_text="Domény na kterých bude web server naslouchat oddělené mezerou. Například 'rosti.cz www.rosti.cz ' apod. První doména je brána jako hlavní.")
	
	documentRoot	= models.CharField(_(u"DocumentRoot"), max_length=200,blank=True)
	htaccess		= models.BooleanField(_(u"htaccess"), default=True)
	indexes			= models.BooleanField(_(u"Index adresáře"), default=True)
	allow_ips	    = models.TextField(_(u"Whitelist"), default="", blank=True)
	deny_ips	    = models.TextField(_(u"Blacklist"), default="", blank=True, help_text=_("One IP per one line"))

	script		    = models.CharField(_(u"Script"), max_length=100)
	processes   	= models.IntegerField(_(u"Počet procesů"), default=1)
	threads	    	= models.IntegerField(_(u"Počet threadů"), default=5)
	virtualenv  	= models.CharField(_(u"Virtualenv"), default="default", max_length=100)
	static	    	= models.TextField(_(u"Statická data"), default="", blank=True)
	python_path	    = models.TextField(_(u"Python path"), default="", blank=True)

	extra           = models.TextField(_(u"Extra configuration"), blank=True, null=True, default="")

	removed			= models.BooleanField(_(u"Smazáno"),default=False) # nezmizí dokud se nezaplatí
	owner			= models.ForeignKey(user, verbose_name=_('Uživatel'))

	@property
	def serverNameSlugged(self):
		return slugify(self.serverName)

	@property
	def pythonPathList(self):
		return [x.strip() for x in self.python_path.split("\n") if x.strip()]

	@property
	def staticList(self):
		statics = []
		for line in self.static.split("\n"):
			line = line.strip().split(" ")
			if len(line) == 2:
				statics.append({"url": line[0], "dir": self.owner.parms.home+""+line[1]})
		return statics

	@property
	def serverName(self):
		domains = self.domains.split(" ")
		if len(domains) > 0:
			return domains[0]
		else:
			return "no-domain"

	@property
	def serverAlias(self):
		domains = self.domains.split(" ")
		if len(domains) > 0:
			return " ".join(domains[1:])
		else:
			return ""

	@property
	def pidfile(self):
		return self.owner.parms.home+"/uwsgi/%s.pid" % self.serverName

	@property
	def logfile(self):
		return self.owner.parms.home+"/uwsgi/%s.log" % self.serverName

	@property
	def socket(self):
		return self.owner.parms.home+"/uwsgi/%s.sock" % self.serverName

	@property
	def virtualenv_path(self):
		return self.owner.parms.home+"/virtualenvs/%s" % self.virtualenv

	@property
	def fastcgiWrapper(self):
		return settings.PCP_SETTINGS["fastcgi_wrapper"] % self.owner

	@property
	def pay(self):
		"""
			Výpočítá cenu stránky za den včetně slevy
		"""
		if self.owner.parms.fee:
			return 0
			
		if self.type == "uwsgi" or self.type == "modwsgi":
			return (settings.PAYMENT_WSGI[self.owner.parms.currency]/30.0)*self.owner.parms.dc()
		elif self.type == "php":
			return (settings.PAYMENT_PHP[self.owner.parms.currency]/30.0)*self.owner.parms.dc()
		else:
			return (settings.PAYMENT_STATIC[self.owner.parms.currency]/30.0)*self.owner.parms.dc()
	
	def __repr__(self):
		return "<Web %s>" % self.serverName
	def __unicode__(self):
		return "%s" % (self.serverName)

class form_static(forms.Form):
	domains		= forms.CharField(label=_(u"Domény *"),help_text=_(u"<br />Domény na kterých bude web server naslouchat oddělené mezerou. Například 'rosti.cz www.rosti.cz ' apod. První doména je brána jako hlavní."))
	documentRoot	= forms.ChoiceField(label=_(u"Adresář"))

class form_wsgi(forms.Form):
	domains		= forms.CharField(label=_(u"Domény *"),help_text=_(u"<br />Domény na kterých bude web server naslouchat oddělené mezerou. Například 'rosti.cz www.rosti.cz ' apod. První doména je brána jako hlavní."))
	static		= forms.CharField(label=_(u"Adresáře se statickými soubory"), widget=forms.Textarea, help_text=_(u"<br /><strong>~/&lt;zadaná_cesta&gt;</strong> - Jeden řádek, jeden adresář. Formát <strong>/url/ /cesta/k/mediím/</strong> - Odělovačem je mezera. Chybné řádky budou při generování konfigurace ignorovány."), required=False)
	python_path	= forms.CharField(label=_(u"Python path"), widget=forms.Textarea, help_text=_(u"<br /><strong>~/&lt;zadaná_cesta&gt;</strong> - Jeden řádek, jeden adresář. Formát <strong>/tady/je/moje/aplikace</strong>. Váš domovský adresář bude automaticky doplněn. uWSGI ignoruje nastavení PYTHON_PATH přes sys.path."), required=False)
	virtualenv	= forms.ChoiceField(label=_(u"Virtualenv *"),choices=(("default","default"),), initial="default", help_text=_(u"<br />Pythoní virtuální prostředí. Najdete je ve '<strong>~/virtualenvs/&lt;zadaná_hodnota&gt;</strong>'. Můžete si si vytvořit vlastní přes SSH."), required=True)
	script		= forms.ChoiceField(label=_(u"WSGI skript *"))
	allow_ips	= forms.CharField(label=_(u"Povolené IPv4 adresy"), widget=forms.Textarea, help_text=_(u"<br />Jedna IP adresa na jeden řádek. Pokud je pole prázdné, fungují všechny."), required=False)

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
