from django.core.management.base import BaseCommand
from wsgiadmin.requests.request import SSHHandler
from wsgiadmin.clients.models import Machine
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Commits performed user actions"

    def handle(self, *args, **options):
        m = Machine.objects.filter(name="illusio")[0]
        u = User.objects.filter(username="cx")[0]
        sh = SSHHandler(u, m)
        sh.commit()
