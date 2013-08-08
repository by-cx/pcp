import datetime
import sys
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wsgiadmin.stats.tools import add_credit
from wsgiadmin.emails.models import Message


class Command(BaseCommand):
    help = "Credit level reminder"

    def remind_user(self, user, parms):
        correction = 0.0
        if parms.credit < 0:
            correction += abs(parms.credit)

        tmpl, data = None, None

        if parms.low_level_credits == "send_email" or parms.num_reminds > 0:
            tmpl = "low_credit"
            data = {"credit": parms.credit, "days": parms.days_left}
        elif parms.low_level_credits == "buy_month":
            data = {"credit": parms.credit, "days": parms.days_left}
            credits = parms.pay_total_day() * 30 + correction
            add_credit(user, credits)
            tmpl = "autobuy_credit"
        elif parms.low_level_credits == "buy_three_months":
            data = {"credit": parms.credit, "days": parms.days_left}
            credits = parms.pay_total_day() * 90 + correction
            add_credit(user, credits)
            tmpl = "autobuy_credit"
        elif parms.low_level_credits == "buy_six_months":
            data = {"credit": parms.credit, "days": parms.days_left}
            credits = parms.pay_total_day() * 180 + correction
            add_credit(user, credits)
            tmpl = "autobuy_credit"
        elif parms.low_level_credits == "buy_year":
            data = {"credit": parms.credit, "days": parms.days_left}
            credits = parms.pay_total_day() * 360 + correction
            add_credit(user, credits)
            tmpl = "autobuy_credit"

        if tmpl and data:
            message = Message.objects.filter(purpose=tmpl)
            if message:
                message[0].send(user.email, data)
                sys.stdout.write("%s reminded\n" % user.username)
        parms.last_notification = datetime.date.today()
        parms.num_reminds += 1
        parms.save()

    def check_user(self, user, parms):
        if (parms.credit - parms.pay_total_day()) <= settings.CREDIT_TRESHOLD and parms.last_notification != datetime.date.today():
            self.remind_user(user, parms)
        elif parms.credit > settings.CREDIT_TRESHOLD and parms.num_reminds > 0:
            parms.num_reminds = 0
            parms.save()

    def handle(self, *args, **options):
        for user in User.objects.all():
            parms = user.parms
            if parms.guard_enable:
                self.check_user(user, parms)
