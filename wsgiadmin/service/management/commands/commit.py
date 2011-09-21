from django.conf import settings
from django.core.management.base import BaseCommand
from wsgiadmin.requests.request import SSHHandler
from wsgiadmin.clients.models import Machine
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Commits performed user actions"

    def handle(self, *args, **options):
        m = Machine.objects.all()[0]
        u = User.objects.all()[0]
        sh = SSHHandler(u, m)
        sh.commit()
