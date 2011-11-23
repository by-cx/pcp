import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.query_utils import Q
from wsgiadmin.apacheconf.models import UserSite
from wsgiadmin.stats.models import Record

class Command(BaseCommand):
    help = "Update user homes size"

    def handle(self, *args, **options):
        with transaction.commit_on_success():
            for record in Record.objects.filter(Q(service="modwsgi") |
                                                Q(service="uwsgi") |
                                                Q(service="php") |
                                                Q(service="static")
            ).filter(cost__lte=0):
                domain = record.value.split(" ")[0]
                site = UserSite.objects.filter(domains__contains=domain)
                if site:
                    site = site[0]
                    record.cost = site.pay
                    record.save(False)
                    print record.cost, "credits for", domain
