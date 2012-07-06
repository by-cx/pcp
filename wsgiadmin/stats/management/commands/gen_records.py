from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wsgiadmin.apacheconf.models import UserSite
from wsgiadmin.stats.models import RecordExists, Record

class RecordUser(object):
    def __init__(self, user):
        self.user = user
        self.gen()

    def gen(self):
        self.record_sites()
        self.record_emails()
        self.record_ftps()
        self.record_mysql()
        self.record_pgsql()
        self.record_fee()

    def _record(self, service, value, cost=0):
        record = Record()
        record.date = date.today()
        record.user = self.user
        record.service = service
        record.value = value
        record.cost = cost
        try:
            record.save()
        except RecordExists:
            pass

    def record_sites(self):
        fee = self.user.parms.fee
        for site in self.user.usersite_set.filter(type="modwsgi"):
            self._record("modwsgi", "%s (%d proc.)" % (site.main_domain.name, site.processes), site.pay if fee <= 0 else 0.0)
        for site in self.user.usersite_set.filter(type="uwsgi"):
            self._record("uwsgi", "%s (%d proc.)" % (site.main_domain.name, site.processes), site.pay if fee <= 0 else 0.0)
        for site in self.user.usersite_set.filter(type="php"):
            self._record("php", site.main_domain.name, site.pay if fee <= 0 else 0.0)
        for site in self.user.usersite_set.filter(type="static"):
            self._record("static", site.main_domain.name, site.pay if fee <= 0 else 0.0)

    def record_emails(self):
        total = 0
        for domain in self.user.domain_set.all():
            total += domain.email_set.count()
        self._record("email", "%d" % total)

    def record_ftps(self):
        self._record("ftp", "%d" % self.user.ftp_set.count())

    def record_mysql(self):
        self._record("mysql", "%d" % self.user.mysqldb_set.count())

    def record_pgsql(self):
        self._record("pgsql", "%d" % self.user.pgsql_set.count())

    def record_fee(self):
        if self.user.parms.fee:
            self._record("fee", "1", float(self.user.parms.fee) / 30.0)

class Command(BaseCommand):
    help = "Create records"

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            RecordUser(user)

        for site in UserSite.objects.all():
            site.delete()

