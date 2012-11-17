import json
from django.contrib.auth.models import User
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from wsgiadmin.clients.models import Address

class Command(BaseCommand):
    args = ""
    help = "Load addresses from PCPInvoice's json"

    def handle(self, *args, **options):
        address_json = os.path.join(settings.ROOT, "..", "migration", "address.json")
        with open(address_json) as f:
            data = json.load(f)

        for user in User.objects.all():
            for address in data:
                address = address["fields"]
                if address.get("email") == user.email and address.get("config") == 1:
                    print "%s %s" % (address.get("first_name"), address.get("last_name"))
                    new_address = Address()
                    new_address.default = True
                    if Address.objects.filter(user=user).count() > 0:
                        new_address.default = False
                    new_address.company = address.get("company")
                    new_address.first_name = address.get("first_name")
                    new_address.last_name = address.get("last_name")
                    new_address.street = address.get("street")
                    new_address.city = address.get("city")
                    new_address.zip = address.get("zip")

                    new_address.phone = address.get("phone")
                    new_address.email = address.get("email")

                    new_address.company_number = address.get("company_number")
                    new_address.vat_number = address.get("vat_number")

                    new_address.user = user
                    new_address.save()
                    break
