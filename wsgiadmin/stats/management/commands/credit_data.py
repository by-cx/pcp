from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import json


class Command(BaseCommand):
    help = "Create records"

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
        invoices = []
        users = User.objects.all()
        for user in users:
            credits = []
            invoice = {}
            for credit in user.credit_set.filter(invoice=False):
                credits.append((credit.date.strftime("%Y-%m-%d"), credit.value - credit.bonus))
                credit.invoice = True
                credit.save()
            invoice["address"] = self.get_address(user)
            invoice["credits"] = credits
            if credits:
                invoices.append(invoice)
        print json.dumps(invoices, sort_keys=True, indent=4)
