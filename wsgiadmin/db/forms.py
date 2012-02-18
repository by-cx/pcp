from django import forms
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.db.models import MySQLDB, PGSQL
from wsgiadmin.service.forms import PassCheckModelForm, RostiFormHelper


class MysqlForm(PassCheckModelForm):

    dbname_max_length = 8
    db_type = 'mysql'

    class Meta:
        model = MySQLDB
        fields = ( 'dbname', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        if 'dbname' in kwargs:
            self.db_name = kwargs.pop('dbname')

        super(MysqlForm, self).__init__(*args, **kwargs)

        self.helper = RostiFormHelper()


    def clean_dbname(self):
        prefix = self.cleaned_data['db_name'].find('_') + 1
        if len(self.cleaned_data["db_name"][prefix:]) > self.dbname_max_length:
            raise forms.ValidationError(_("Database name can contains max. %s characters" % self.dbname_max_length))

        return self.cleaned_data["db_name"]

class PgsqlForm(MysqlForm):

    db_type = 'pg'

    class Meta:
        model = PGSQL
        fields = ( 'dbname', 'password1', 'password2')
