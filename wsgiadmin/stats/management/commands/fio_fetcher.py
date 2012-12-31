from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

url = "https://www.fio.cz/ib_api/rest/periods/%(token)s/%(date_from)s/%(date_to)s/transactions.json"

class Command(BaseCommand):
    help = "Create records"

    def handle(self, *args, **options):
        pass
