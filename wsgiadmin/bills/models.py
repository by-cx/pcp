# -*- coding: utf-8 -*-

from django.contrib.auth.models import User as user
from django.db import models
from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

class balance(models.Model):
	user		= models.ForeignKey(user, primary_key=True)
	bills       = models.FloatField(_(u"Celkem účty"))
	incomes     = models.FloatField(_(u"Celkem příjmy"))
	sum         = models.FloatField(_(u"Balance"))

	class Meta:
		managed = False
		db_table = "balance"

	def __unicode__(self):
		return "%s (%f)" % (self.user.username, self.sum)

class income(models.Model):
	pub_date	= models.DateTimeField(auto_now_add=True)
	cash        = models.FloatField(_(u"Částka"))
	note        = models.CharField(_(u"Poznámka"), max_length=1024)
	currency    = models.CharField(_(u"Měna"), max_length=20, choices=settings.CURRENCY)

	user		= models.ForeignKey(user)

	def __unicode__(self):
		return "%s: %f (%s)" % (self.user.username, self.cash, self.pub_date)

class bill(models.Model):
	pub_date	= models.DateTimeField(auto_now_add=True)
	price		= models.FloatField(_(u"Částka"))
	info		= models.CharField(_(u"Doplňující informace"),max_length=250)
	processed	= models.BooleanField(_(u"Zpracováno do faktury"),default=False)
	currency    = models.CharField(_(u"Měna"), max_length=20, choices=settings.CURRENCY)
	
	user		= models.ForeignKey(user)
	
	def __unicode__(self):
		return "%s - %s (%f)"%(str(self.pub_date),self.info,self.price)

class form_bill(ModelForm):
	class Meta:
		model = bill

EVERY = (
			("day",_(u"Denně")),
			("week",_(u"Týdně")),
			("month",_(u"Měsíčně")),
			("3months",_(u"Čtvrtletně")),
			("6months",_(u"Půlročně")),
			("9months",_(u"3/4 letně")),
			("year",_(u"Ročně")),
)

class service(models.Model):
	info		= models.CharField(_(u"Doplňující služba"),max_length=250)
	price		= models.FloatField(_(u"Částka"))
	every		= models.CharField(_(u"Platba za"),choices=EVERY,max_length=250)
	
	user		= models.ForeignKey(user)
	
	def one_day_price(self):
		days = {
			"day":1.0,
			"week":7.0,
			"month":30.0,
			"3months":91.0,
			"6months":182.0,
			"9months":273.0,
			"year":365.0,
		}
		
		return self.price/days[self.every]
	
	def __unicode__(self):
		return "%s - %s (%f)"%(self.user.username,self.info,self.price)
	
class form_service(ModelForm):
	class Meta:
		model = service
