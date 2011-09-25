from django import forms
from django.forms import models
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.db.models import MySQLDB, PGSQL

class MysqlForm(models.ModelForm):

    password = forms.CharField(label=_("Database password"), widget=forms.PasswordInput)

    dbname_max_length = 8
    pwd_min_length = 6


    class Meta:
        model = MySQLDB
        fields = ( 'dbname', 'password',)

    def clean_dbname(self):
        prefix = self.cleaned_data['dbname'].find('_') + 1
        if len(self.cleaned_data["dbname"][prefix:]) > self.dbname_max_length:
            raise forms.ValidationError(_("Database name can contains max. %s characters" % self.dbname_max_length))

        return self.cleaned_data["dbname"]

    def clean_password(self):
        if len(self.cleaned_data["password"]) < self.pwd_min_length:
            raise forms.ValidationError(_("Min. length of password is %s chars" %  self.pwd_min_length))

        return self.cleaned_data["password"]


class PgsqlForm(MysqlForm):

    class Meta:
        model = PGSQL
        fields = ( 'dbname', 'password',)
