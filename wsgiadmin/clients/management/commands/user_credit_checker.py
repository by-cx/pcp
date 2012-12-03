from constance import config
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from wsgiadmin.apacheconf.tools import restart_master
from wsgiadmin.emails.models import Message

class Command(BaseCommand):
    args = ""
    help = "Command to automatic enable/disable users based on credit balance. Need to be call every day."

    def handle(self, *args, **options):
        for user in User.objects.all():
            change = False
            if user.parms.credit < 0 and user.parms.enable and user.parms.guard_enable:
                print "Disable: %s (%.2f)" % (user.username, user.parms.credit)
                user.parms.enable = False
                change = True
                apps = [app.main_domain.domain_name for app in user.usersite_set.all()]
                msg = Message.objects.get(purpose="webs_disabled")
                msg.send(user.email, {"apps": "\n".join(apps), "username": user.username})
            elif user.parms.credit > 0 and not user.parms.enable and user.parms.guard_enable:
                print "Enable: %s (%.2f)" % (user.username, user.parms.credit)
                user.parms.enable = True
                change = True
                msg = Message.objects.get(purpose="webs_enabled")
                msg.send(user.email, {"username": user.username})
            #if change:
                #restart_master(config.mode, user)
                #user.parms.save()
