from datetime import date
import json
import pickle
import re
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from wsgiadmin.stats.models import Record

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

    def get_address(self, user):
        if user.parms.address.invoice_name:
            if len(user.parms.address.invoice_name.split(" ")) >= 2:
                first_name = user.parms.address.invoice_name.split(" ")[0]
                last_name = user.parms.address.invoice_name.split(" ")[1]
            else:
                first_name = user.parms.address.invoice_name.split(" ")[0]
                last_name = ""
            address = {
                "company": user.parms.address.company,
                "first_name": first_name,
                "last_name": last_name,
                "street": user.parms.address.invoice_street,
                "city": user.parms.address.invoice_city,
                "zip": user.parms.address.invoice_city_num,
                "phone": user.parms.address.invoice_phone,
                "email": user.parms.address.invoice_email,
                "company_number": user.parms.address.residency_ic,
                "vat_number": user.parms.address.residency_dic,
            }
        else:
            if len(user.parms.address.residency_name.split(" ")) >= 2:
                first_name = user.parms.address.residency_name.split(" ")[0]
                last_name = user.parms.address.residency_name.split(" ")[1]
            else:
                first_name = user.parms.address.residency_name.split(" ")[0]
                last_name = ""
            address = {
                "company": user.parms.address.company,
                "first_name": first_name,
                "last_name": last_name,
                "street": user.parms.address.residency_city,
                "city": user.parms.address.residency_city,
                "zip": user.parms.address.residency_city_num,
                "phone": user.parms.address.residency_phone,
                "email": user.parms.address.residency_email,
                "company_number": user.parms.address.residency_ic,
                "vat_number": user.parms.address.residency_dic,
            }
        return address

    def handle(self, *args, **options):
        month, year = self.get_date(args)

        users = User.objects.all()
        reports = []
        for user in users:
            report = {"webs": []}
            records = self.get_records(user, month, year)
            last = None
            web_record = {}
            record = None
            for record in records:
                if last and record.value != last.value:
                    if web_record:
                        web_record["date_end"] = last.date.strftime("%Y-%m-%d")
                        report["webs"].append(web_record)
                    web_record = {"date_start": record.date.strftime("%Y-%m-%d"), "date_end": record.date.strftime("%Y-%m-%d"), "service": record.service,
                                  "domain": record.value}
                    proc = re.findall("\(([0-9]+) proc.\)", record.value)
                    if proc:
                        web_record["processes"] = proc[0]
                last = record
            if record and web_record:
                web_record["date_end"] = record.date.strftime("%Y-%m-%d")
                report["webs"].append(web_record)
            report["address"] = self.get_address(user)
            report["fee"] = user.parms.fee
            report["discount"] = user.parms.discount
            if report["webs"]:
                reports.append(report)
            print json.dumps(reports)
