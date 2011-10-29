from datetime import date
import pickle
import re
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from wsgiadmin.stats.models import Record

class Report(object):
    def __init__(self):
        self.webs = []
        self.address = []

    def __unicode__(self):
        return u", ".join([web.domain for web in self.webs])
    def __str__(self):
        return ", ".join([web.domain for web in self.webs])

class WebRecord(object):
    def __init__(self):
        self.date_start = None
        self.date_end = None
        self.service = ""
        self.domain = ""
        self.processes = 0

    def __unicode__(self):
        s = u"%s - %s\n" % (self.date_start, self.date_end)
        s += u"%s %s" % (self.service, self.domain)
        return s
    def __str__(self):
        s = "%s - %s\n" % (self.date_start, self.date_end)
        s += "%s %s" % (self.service, self.domain)
        return s

class Command(BaseCommand):
    help = "Generate report for invoice system. Optionaly, you can give MM/YYYY format, otherwise get actual month"

    def get_records(self, user, month=date.today().month, year=date.today().year):
        records = list(Record.objects.filter(user=user, date__month=month, date__year=year,
                                             service="modwsgi").order_by("value", "date")) + \
                  list(Record.objects.filter(user=user, date__month=month, date__year=year,
                                             service="uwsgi").order_by("value", "date")) + \
                  list(Record.objects.filter(user=user, date__month=month, date__year=year,
                                             service="php").order_by("value", "date")) + \
                  list(Record.objects.filter(user=user, date__month=month, date__year=year,
                                             service="static").order_by("value", "date"))
        return records

    def get_date(self, args):
        month = date.today().month
        year = date.today().year
        if len(args) and re.match("([0-9]{1,2})/([0-9]{4})", args[0]):
            s = re.match("([0-9]{1,2})/([0-9]{4})", args[0])
            month = s.groups()[0]
            year = s.groups()[1]
        return month, year

    def handle(self, *args, **options):
        month, year = self.get_date(args)

        users = User.objects.all()
        reports = []
        for user in users:
            report = Report()
            records = self.get_records(user, month, year)
            last = None
            web_record = None
            record = None
            for record in records:
                if last and record.value != last.value:
                    if web_record:
                        web_record.date_end = last.date
                        report.webs.append(web_record)
                    web_record = WebRecord()
                    web_record.date_start = record.date
                    web_record.date_end = record.date
                    web_record.service = record.service
                    web_record.domain = record.value
                    proc = re.findall("\(([0-9]+) proc.\)", record.value)
                    if proc:
                        web_record.processes = proc[0]
                last = record
            if record and web_record:
                web_record.date_end = record.date
                report.webs.append(web_record)
            report.address = user.parms.address
            report.fee = user.parms.fee
            report.discount = user.parms.discount
            if report.webs:
                reports.append(report)
            print pickle.dumps(reports)
