# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django import forms

import re

class form_static(forms.Form):
    domains = forms.CharField(label=_(u"Domény *"), help_text=_(u"<br />Domény na kterých bude web server naslouchat oddělené mezerou. Například 'rosti.cz www.rosti.cz ' apod. První doména je brána jako hlavní."))
    documentRoot = forms.ChoiceField(label=_(u"Adresář"))


class form_wsgi(forms.Form):
    domains = forms.CharField(label=_(u"Domény *"), help_text=_(
        u"<br />Domény na kterých bude web server naslouchat oddělené mezerou. Například 'rosti.cz www.rosti.cz ' apod. První doména je brána jako hlavní."))
    static = forms.CharField(label=_(u"Adresáře se statickými soubory"), widget=forms.Textarea, help_text=_(
        u"<br /><strong>~/&lt;zadaná_cesta&gt;</strong> - Jeden řádek, jeden adresář. Formát <strong>/url/ /cesta/k/mediím/</strong> - Odělovačem je mezera. Chybné řádky budou při generování konfigurace ignorovány.")
        , required=False)
    python_path = forms.CharField(label=_(u"Python path"), widget=forms.Textarea, help_text=_(
        u"<br /><strong>~/&lt;zadaná_cesta&gt;</strong> - Jeden řádek, jeden adresář. Formát <strong>/tady/je/moje/aplikace</strong>. Váš domovský adresář bude automaticky doplněn.<br />uWSGI ignoruje nastavení PYTHON_PATH přes sys.path.")
        , required=False)
    virtualenv = forms.ChoiceField(label=_(u"Virtualenv *"), choices=(("default", "default"),), initial="default",
        help_text=_(
            u"<br />Pythoní virtuální prostředí. Najdete je ve '<strong>~/virtualenvs/&lt;zadaná_hodnota&gt;</strong>'. Můžete si si vytvořit vlastní přes SSH.")
        , required=True)
    script = forms.ChoiceField(label=_(u"WSGI skript *"))
    allow_ips = forms.CharField(label=_(u"Povolené IPv4 adresy"), widget=forms.Textarea,
        help_text=_(u"<br />Jedna IP adresa na jeden řádek. Pokud je pole prázdné, fungují všechny."), required=False)

    def clean_allow_ips(self):
        ips = [x.strip() for x in self.cleaned_data["allow_ips"].split("\n") if x.strip()]

        for ip in ips:
            if not re.match("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip):
                raise forms.ValidationError(_(u"Jedna nebo více zadaných IP adres má špatný tvar"))

        return self.cleaned_data["allow_ips"]

    def clean_virtualenv(self):
        if "." in self.cleaned_data["virtualenv"] or \
           "~" in self.cleaned_data["virtualenv"] or \
           "/" in self.cleaned_data["virtualenv"]:
            raise forms.ValidationError(_(u"Virtualenv nesmí obsahovat znaky ./~"))
        return self.cleaned_data["virtualenv"]

    def clean_static(self):
        if ".." in self.cleaned_data["static"] or \
           "~" in self.cleaned_data["static"]:
            raise forms.ValidationError(_(u"Toto pole nesmí obsahovat nesmí obsahovat .. a ~"))
        return self.cleaned_data["static"]
