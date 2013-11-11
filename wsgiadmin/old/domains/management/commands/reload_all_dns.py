import logging
from django.core.management.base import BaseCommand, CommandError
from wsgiadmin.old.domains.models import Domain
from wsgiadmin.old.requests.request import BindRequest

class Command(BaseCommand):
    args = ""
    help = "Update all old DNS records"


    def handle(self, *args, **options):
        domains = Domain.objects.all()
        for domain in domains:
            if domain.dns:
                pri_br = BindRequest(domain.owner, "master")
                pri_br.mod_zone(domain)
                pri_br.mod_config()
                pri_br.reload()
                sec_br = BindRequest(domain.owner, "slave")
                sec_br.mod_config()
                sec_br.reload()

