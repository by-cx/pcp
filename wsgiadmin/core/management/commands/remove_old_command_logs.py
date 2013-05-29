import datetime
from django.core.management.base import BaseCommand
from wsgiadmin.core.models import CommandLog


class Command(BaseCommand):
    args = ""
    help = "Remove old CommandLogs. Put it in per day cron."

    def handle(self, *args, **options):
        week_ago = datetime.datetime.now() - datetime.timedelta(7)
        CommandLog.objects.filter(date__lt=week_ago).delete()