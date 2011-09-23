from django import forms
from django.forms import models
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.db.models import MySQLDB, PGSQL

class MysqlForm(models.ModelForm):

    password = forms.CharField(label=_("Database password"), widget=forms.PasswordInput)

    class Meta:
        model = MySQLDB
        fields = ( 'dbname', 'password',)

    def clean_database(self):
        if len(self.cleaned_data["database"]) > 8:
            raise forms.ValidationError(_("Database name can contains max. 8 characters"))

        return self.cleaned_data["database"]

    def clean_password(self):
        if len(self.cleaned_data["password"]) < 6:
            raise forms.ValidationError(_("Min. length of password is 6 chars"))
        return self.cleaned_data["password"]


class PgsqlForm(MysqlForm):

    class Meta:
        model = PGSQL
        fields = ( 'dbname', 'password',)
