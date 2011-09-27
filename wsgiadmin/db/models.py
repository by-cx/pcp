from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class MySQLDB(models.Model):
    dbname = models.CharField(_("Name of MySQL database"), max_length=50, unique=True)
    owner = models.ForeignKey(User, verbose_name=_("User"))

    class Meta:
        db_table = 'mysql_mysqldb'

    def __unicode__(self):
        return "%s (%s)" % (self.dbname, self.owner)


class PGSQL(models.Model):
    dbname = models.CharField(_("Name of PgSQL database"), max_length=50, unique=True)
    owner = models.ForeignKey(User, verbose_name=_("User"))

    class Meta:
        db_table = 'pgs_pgsql'

    def __unicode__(self):
        return "%s (%s)" % (self.dbname, self.owner)
