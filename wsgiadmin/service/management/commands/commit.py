from django.conf import settings
from django.core.management.base import BaseCommand
from wsgiadmin.requests.request import SSHHandler
from wsgiadmin.clients.models import Machine
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Commits performed user actions"

    def handle(self, *args, **options):
        m = Machine.objects.filter(name=settings.COMMIT_MACHINE)
        u = User.objects.filter(username=settings.COMMIT_USER)
        sh = SSHHandler(u, m)
        sh.commit()
