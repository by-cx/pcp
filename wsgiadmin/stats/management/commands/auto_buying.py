import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wsgiadmin.emails.models import Message

class Command(BaseCommand):
    help = "Autobying of credit - work's fine with cron"

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            last_notification = user.parms.last_notification if user.parms.last_notification else datetime.date(1970, 1 ,1)
            if user.parms.credit < 15 and user.parms.pay_total_day() > 0 and (datetime.date.today() - last_notification).days > 14:
                if user.parms.low_level_credits == "send_email":
                    if not user.email: continue
                    message = Message.objects.filter(purpose="low_credit")
                    if message:
                        message[0].send(user.email)
                elif user.parms.low_level_credits == "buy_month":
                    total = user.parms.pay_total_day() * 30
                    user.parms.add_credit(total)
                    if not user.email: continue
                    message = Message.objects.filter(purpose="autobuy_credit")
                    if message:
                        message[0].send(user.email)
                elif user.parms.low_level_credits == "buy_three_months":
                    total = user.parms.pay_total_day() * 90
                    user.parms.add_credit(total)
                    if not user.email: continue
                    message = Message.objects.filter(purpose="autobuy_credit")
                    if message:
                        message[0].send(user.email)
                elif user.parms.low_level_credits == "buy_six_months":
                    total = user.parms.pay_total_day() * 180
                    user.parms.add_credit(total)
                    if not user.email: continue
                    message = Message.objects.filter(purpose="autobuy_credit")
                    if message:
                        message[0].send(user.email)
                elif user.parms.low_level_credits == "buy_year":
                    total = user.parms.pay_total_day() * 360
                    user.parms.add_credit(total)
                    if not user.email: continue
                    message = Message.objects.filter(purpose="autobuy_credit")
                    if message:
                        message[0].send(user.email)

                user.parms.last_notification = datetime.date.today()
                user.parms.save()