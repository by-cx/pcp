import json
from django.contrib.auth.models import User
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from wsgiadmin.dns.backend import DomainObject
from wsgiadmin.dns.models import Domain

class Command(BaseCommand):
    args = ""
    help = "Regenerate all zones"

    def handle(self, *args, **options):
        for domain in Domain.objects.all():
            script = DomainObject()
            script.update(domain)
            script.commit()
        script.reload()

