from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wsgiadmin.stats.models import RecordExists, Record

class RecordUser(object):
    def __init__(self, user):
        self.user = user
        self.gen()

    def gen(self):
        self.record_sites()
        self.record_apps()
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
        total = 0.0
        for site in self.user.usersite_set.all():
            total += site.pay
        if total:
            self._record("old_webs", "Old websites", total if fee <= 0 else 0.0)

    def record_apps(self):
        fee = self.user.parms.fee
        total = 0.0
        for app in self.user.app_set.all():
            total += app.price
        if total:
            self._record("apps", "Apps", total if fee <= 0 else 0.0)

    def record_fee(self):
        if self.user.parms.fee:
            self._record("fee", "Fee", float(self.user.parms.fee) / 30.0)

class Command(BaseCommand):
    help = "Create records"

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            RecordUser(user)

