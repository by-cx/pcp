from datetime import date
from wsgiadmin.clients.models import Parms
from wsgiadmin.emails.models import Message
from wsgiadmin.stats.models import Record

def pay(user, service, value, cost):
    record = Record()
    record.date = date.today()
    record.user = user
    record.service = service
    record.value = value
    record.cost = cost
    record.save()

def low_credits_level():
    for parm in Parms.objects.all():
        credit = parm.credit
        pay_per_day = parm.pay_total_day()

        if parm.user.username != "cx": continue

        if parm.last_notification and (date.today() - parm.last_notification).days < 14:
            continue

        #TODO:how to work with credit < 0 and pay_per_day == 0?
        if (credit < 0 and pay_per_day > 0) or (pay_per_day > 0 and credit / pay_per_day <= 14):
            if parm.low_level_credits == "send_email":
                message = Message.objects.get(purpose="low_credit")
                message.send(parm.address.residency_email, {"username": parm.user.username, "credit": credit, "days": int(credit / pay_per_day)})
            elif parm.low_level_credits == "buy_month":
                parm.add_credit(pay_per_day * 30)
            elif parm.low_level_credits == "buy_three_months":
                parm.add_credit(pay_per_day * 90)
            elif parm.low_level_credits == "buy_six_months":
                parm.add_credit(pay_per_day * 180)
            elif parm.low_level_credits == "buy_year":
                parm.add_credit(pay_per_day * 360)

        parm.last_notification = date.today()
        parm.save()
