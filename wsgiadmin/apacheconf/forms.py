# -*- coding: utf-8 -*-

import re

from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.apacheconf.models import UserSite
from wsgiadmin.apacheconf.tools import get_user_wsgis, get_user_venvs


class form_static(forms.Form):
    domains = forms.CharField(label=_(u"Domény *"), help_text=_(u"<br />Domény na kterých bude web server naslouchat oddělené mezerou. Například 'rosti.cz www.rosti.cz ' apod. První doména je brána jako hlavní."))
    documentRoot = forms.ChoiceField(label=_(u"Adresář"))


class FormWsgi(ModelForm):

    class Meta:
        model = UserSite
        fields = ('domains', 'static', 'python_path', 'virtualenv', 'script', 'allow_ips')
        widgets = {
            'static': forms.Textarea,
            'python_path': forms.Textarea,
            'allow_ips': forms.Textarea,
            'virtualenv': forms.Select,
            'script': forms.Select,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super(FormWsgi, self).__init__(*args, **kwargs)

        self.fields['domains'].help_text = _(u"<br />Domény na kterých bude web server naslouchat oddělené mezerou. Například 'rosti.cz www.rosti.cz ' apod. První doména je brána jako hlavní.")
        self.fields['static'].help_text = _(u"<br />Formát <strong>/url/ /cesta/k/mediím/</strong>, odděleno mezerou.<br /><ul><li>/cesta/k/mediím/ je prefixnuta domovským adresářem</li><li>1 řádek může obsahovat právě 1 adresář</li><li>Chybné řádky budou ignorovány</li></ul>.")
        self.fields['python_path'].help_text=_(u"<br /><strong>~/&lt;zadaná_cesta&gt;</strong> - Jeden řádek, jeden adresář. Formát <strong>/tady/je/moje/aplikace</strong>. Váš domovský adresář bude automaticky doplněn.<br />uWSGI ignoruje nastavení PYTHON_PATH přes sys.path.")
        self.fields['virtualenv'].help_text= _(u"<br />Pythoní virtuální prostředí. Najdete je ve '<strong>~/virtualenvs/&lt;zadaná_hodnota&gt;</strong>'. Můžete si si vytvořit vlastní přes SSH.")
        self.fields['allow_ips'].help_text = help_text=_(u"<br />Jedna IP adresa na jeden řádek. Pokud je pole prázdné, fungují všechny.")

        wsgis = get_user_wsgis(self.user)
        wsgis_choices = [("", _(u"Nevybráno"))] + [(x, x) for x in wsgis]

        virtualenvs = get_user_venvs(self.user)
        virtualenvs_choices = [("", _(u"Nevybráno"))] + [(one, one) for one in virtualenvs]

        self.fields["virtualenv"].widget.choices = virtualenvs_choices
        self.fields['script'].widget.choices = wsgis_choices
        


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
