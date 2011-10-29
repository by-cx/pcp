from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
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

    def _record(self, service, value):
        record = Record()
        record.date = date.today()+timedelta(3)
        record.user = self.user
        record.service = service
        record.value = value
        try:
            record.save()
        except RecordExists:
            pass

    def record_sites(self):
        for site in self.user.usersite_set.filter(type="modwsgi"):
            self._record("modwsgi", "%s (%d proc.)" % (site.server_name, site.processes))
        for site in self.user.usersite_set.filter(type="uwsgi"):
            self._record("uwsgi", "%s (%d proc.)" % (site.server_name, site.processes))
        for site in self.user.usersite_set.filter(type="php"):
            self._record("php", site.server_name)
        for site in self.user.usersite_set.filter(type="static"):
            self._record("static", site.server_name)

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

class Command(BaseCommand):
    help = "Create records"

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            RecordUser(user)

