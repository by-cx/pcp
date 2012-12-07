import logging
from django.core.management.base import BaseCommand, CommandError
from wsgiadmin.apps.models import App
from wsgiadmin.apps.apps import PythonApp, AppObject, typed_object
from wsgiadmin.emails.models import Message

class Command(BaseCommand):
    args = ""
    help = "Update configuration of all apps"

    def handle(self, *args, **options):
        for app in App.objects.all():
            print "%s: %s" % (app.user.username, app.name)
            app = typed_object(app)
            app.update()
            app.commit()
