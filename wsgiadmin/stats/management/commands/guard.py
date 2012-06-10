import datetime
import logging
from constance import config
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wsgiadmin.apacheconf.tools import restart_master
from wsgiadmin.clients.models import Parms
from wsgiadmin.emails.models import Message
from django.db import transaction

info = logging.info

class Command(BaseCommand):
    help = "Credit guardian"

    def get_users(self):
        """Get users close to 0 or under"""
        users = []
        for user in User.objects.all():
            if ( float(user.parms.pay_total_day()) == 0 and user.parms.credit < 0 ) or\
               ( user.parms.pay_total_day() > 0 and float(user.parms.credit) / float(user.parms.pay_total_day()) < 14 ):
                users.append(user)
        return users

    def process(self, user):
        parms = user.parms
        apache_reload = False
        data = {}
        tmpl = ""

        if config.auto_disable:
            if parms.pay_total_day() > 0 and parms.credit >= 0 and (parms.credit / parms.pay_total_day()) < config.credit_threshold and parms.enable:
                parms.enable = False
                parms.save()
                apache_reload = True
                message = Message.objects.filter(purpose="web_disabled")
                if message:
                    message[0].send(user.email, {})
                print "\t* %s disabled" % user.username
            elif parms.credit >= 0 and not parms.enable:
                parms.enable = True
                parms.save()
                apache_reload = True
                print "\t* %s enabled" % user.username

        if parms.low_level_credits == "send_email":
            tmpl = "low_credit"
            data = {"credit": parms.credit, "days": (parms.credit / parms.pay_total_day()) if parms.pay_total_day() > 0 else "0"}
        elif parms.low_level_credits == "buy_month":
            credits = parms.pay_total_day() * 30
            parms.add_credit(credits)
            tmpl = "autobuy_credit"
            data = {"credit": parms.credit, "days": (parms.credit / parms.pay_total_day()) if parms.pay_total_day() > 0 else "0"}
        elif parms.low_level_credits == "buy_three_months":
            credits = parms.pay_total_day() * 90
            parms.add_credit(credits)
            tmpl = "autobuy_credit"
            data = {"credit": parms.credit, "days": (parms.credit / parms.pay_total_day()) if parms.pay_total_day() > 0 else "0"}
        elif parms.low_level_credits == "buy_six_months":
            credits = parms.pay_total_day() * 180
            parms.add_credit(credits)
            tmpl = "autobuy_credit"
            data = {"credit": parms.credit, "days": (parms.credit / parms.pay_total_day()) if parms.pay_total_day() > 0 else "0"}
        elif parms.low_level_credits == "buy_year":
            credits = parms.pay_total_day() * 360
            parms.add_credit(credits)
            tmpl = "autobuy_credit"
            data = {"credit": parms.credit, "days": (parms.credit / parms.pay_total_day()) if parms.pay_total_day() > 0 else "0"}

        if tmpl and data:
            message = Message.objects.filter(purpose=tmpl)
            if message:
                message[0].send(user.email, data)
                message[0].send(config.email, data)
                print "\t* E-mail sent"
            parms.last_notification = datetime.date.today()
            parms.save()

        return apache_reload

    def handle(self, *args, **options):
        total_credit = 0.0
        apache_reload = False
        guarding = []
        for user in self.get_users():
            parms = user.parms
            print user.username.ljust(40),
            print ("%.2f cr." % parms.credit).ljust(15),
            print ("%.2f cr." % parms.pay_total_day()).ljust(10),
            print ("%.2f" % (parms.credit / parms.pay_total_day()) if parms.pay_total_day() > 0 else "0").ljust(10),
            print (parms.low_level_credits).ljust(15),
            print (parms.last_notification.strftime("%d.%m.%Y")).ljust(15) if parms.last_notification else "--".ljust(15),
            if not parms.guard_enable: print "Guarding disabled",
            if parms.credit < 0:
                total_credit += parms.credit
            if not parms.last_notification or (parms.last_notification and (datetime.date.today() - parms.last_notification).days >= 7):
                if parms.guard_enable:
                    guarding.append(user)
                    print "Be guarded",
            print
        print "Total: %.2f" % total_credit

        if raw_input("Do you agree? (yes/NO) ") == "yes":
            for user in guarding:
                with transaction.commit_on_success():
                    apache_reload = self.process(user)
            if apache_reload:
                restart_master(config.mode, user)
                print "Apache restarted"
