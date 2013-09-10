import datetime
import sys
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from fiobank import FioBank
from wsgiadmin.stats.models import TransId
from wsgiadmin.stats.tools import payed


class Command(BaseCommand):
    help = "Check who pay and who dont"

    def pay(self, date, user, value, trans):
        #credits = user.credit_set.filter(date_payed=None, price=value, date__lte=date)
        credits = user.credit_set.filter(date_payed=None, price=value)
        if credits:
            credit = credits[0]
            sys.stdout.write(credit.user.username)
            sys.stdout.write(" ")
            sys.stdout.write(credit.date.strftime("%d.%m.%Y"))
            sys.stdout.write(" ")
            sys.stdout.write("%.2f" % credit.price)
            sys.stdout.write("\n")
            payed(credit)

            transid = TransId()
            transid.trans_id = trans
            transid.credit = credit
            transid.save()


    def handle(self, *args, **options):
        if settings.FIO_TOKEN:
            client = FioBank(token=settings.FIO_TOKEN)
            payments = client.period(from_date=datetime.date.today()-datetime.timedelta(30), to_date=datetime.date.today())
            for payment in payments:
                date = payment.get("date")
                vs = payment.get("variable_symbol")
                value = payment.get("amount", 0.0)
                trans = payment.get("transaction_id")
                if vs and value and date and trans:
                    try:
                        user = User.objects.get(id=(int(vs) - 100000))
                    except ObjectDoesNotExist:
                        continue
                    if not TransId.objects.filter(trans_id=trans).count() and value > 0:
                        self.pay(date, user, value, trans)
        else:
            sys.stderr.write("Error: not FIO TOKEN found")
