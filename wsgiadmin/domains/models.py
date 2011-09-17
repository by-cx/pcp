# -*- coding: utf-8 -*-

import re
from django.db import models
from django import forms
from django.contrib.auth.models import User as user

from django.utils.translation import ugettext_lazy as _

class Domain(models.Model):
    name = models.CharField(_(u"Název domény"), max_length=100, unique=True)
    pub_date = models.DateField(auto_now=True)
    serial = models.IntegerField(_(u"Sériové číslo domény"), default=0)
    dns = models.BooleanField(_(u"Vést DNS záznamy?"), default=True)
    mail = models.BooleanField(_(u"Vést poštu"), default=True)
    ipv4 = models.BooleanField(_(u"IPv4 záznamy"), default=True)
    ipv6 = models.BooleanField(_(u"IPv6 záznamy"), default=True)
    owner = models.ForeignKey(user)

    def __unicode__(self):
        return "%s" % self.name


class registration_request(models.Model):
    name = models.CharField(_(u"Název domény"), max_length=100, unique=True)
    pub_date = models.DateField(auto_now=True)
    kind = models.CharField(_(u"Registrace/transfer"), max_length=20,
        choices=(("registration", _(u"Registrace nové domény")), ("transfer", _(u"Přesunutí existující domény"))))
    ip = models.CharField(_(u"IP adresa ze které šel požadavek"), max_length=50)
    hostname = models.CharField(_(u"Hostname ze kterého šel požadavek"), max_length=50)
    passwd = models.CharField(_(u"Heslo pro transfer"), max_length=100, blank=True)
    years = models.IntegerField(_(u"Počet let"), default=1)
    user = models.ForeignKey(user)

    def __unicode__(self):
        return "%s" % self.name


CHOICES = [(".cz", ".cz"), (".eu", ".eu"), (".cz.cc", ".cz.cc"), (".co.cz", ".co.cz"), (".com", ".com"),
    (".org", ".org"), (".net", ".net"), (".biz", ".biz"), (".info", ".info"), (".name", ".name")]
YEARS = [("1", "1 rok"), ("2", "2 roky"), ("3", "3 roky")]

class form_registration_request(forms.Form):
    domain = forms.CharField(label=_(u"Doména"))
    ipv4 = forms.BooleanField(label="Vést záznamy o IPv4 adresách", required=False, initial=True)
    ipv6 = forms.BooleanField(label="Vést záznamy o IPv6 adresách", required=False, initial=True)

    def clean_domain(self):
        if not re.search("[a-z0-9\-\.]*\.[a-z]{2,5}", self.cleaned_data["domain"]):
            raise forms.ValidationError(_(u"Doména má špatný formát"))

        return self.cleaned_data["domain"]


class form_registration_request_years(forms.Form):
    domain = forms.CharField(label=_(u"Doména"))
    tld = forms.ChoiceField(label=_(u"TLD"), choices=CHOICES, help_text=_(u"Vyberte koncovku"))
    years = forms.ChoiceField(label=_(u"Počet let"), choices=YEARS, required=False)
    passwd = forms.CharField(label=_(u"Heslo pro transfer"), required=False,
        help_text=_(u"Nepovinné. Bude dočasně uloženo v databázi v textové podobě."))

