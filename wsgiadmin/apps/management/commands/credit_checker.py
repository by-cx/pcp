import json
import logging
from django.contrib.auth.models import User
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from wsgiadmin.apps.backend import PythonApp, AppBackend
from wsgiadmin.clients.models import Address
from wsgiadmin.emails.models import Message

class Command(BaseCommand):
    args = ""
    help = "Command to automatic enable/disable app based on credit balance. Need to be call every few minutes."

    def handle(self, *args, **options):
        for user in User.objects.all():
            disabled = []
            enabled = []
            for app in user.app_set.all():
                if user.parms.credit < 0 and not app.disabled:
                    if app.app_type == "python":
                        app = PythonApp.objects.get(id=app.id)
                    else:
                        app = AppBackend.objects.get(id=app.id)
                    app.disable()
                    app.commit()
                    logging.info("%s (%d) disabled" % (app.name, app.id))
                    print "%s (%d) disabled" % (app.name, app.id)
                    disabled.append("* %s" % app.name)
                elif user.parms.credit >= 0 and app.disabled:
                    app.enable()
                    app.commit()
                    logging.info("%s (%d) enabled" % (app.name, app.id))
                    print "%s (%d) enabled" % (app.name, app.id)
                    enabled.append("* %s" % app.name)
            if disabled:
                msg = Message.objects.get(purpose="webs_disabled")
                msg.send(user.email, {"apps": "\n".join(disabled), "username": user.username})
            if enabled:
                msg = Message.objects.get(purpose="webs_enabled")
                msg.send(user.email, {"username": user.username})