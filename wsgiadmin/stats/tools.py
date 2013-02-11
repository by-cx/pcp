from datetime import date, datetime
import json
from constance import config
import requests
from wsgiadmin.clients.models import Parms
from wsgiadmin.emails.models import Message
from wsgiadmin.stats.models import Record, Credit
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __

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

def add_credit(user, value, address=None, free=None):
    value = float(value)

    if not address and not free:
        address = user.address_set.filter(removed=False).get(default=True)

    credit = Credit()
    if not free:
        credit.date_payed = None
    else:
        credit.date_payed = datetime.now()
    print config.credit_currency
    credit.user = user
    credit.price = (1 / float(config.credit_quotient)) * value
    credit.currency = config.credit_currency
    credit.value = value
    credit.bonus = 0
    credit.address = address
    credit.save()

    if address and not free:
        context = {
            "cost": credit.price,
            "currency": credit.currency,
            "bank": config.bank_name,
            "bank_account": config.bank_account,
            "var_symbol": user.parms.var_symbol,
            }
        msg = Message.objects.get(purpose="make_a_payment")
        msg.send(address.email, context)

    return credit

def payed(credit):
    if credit.date_payed or credit.gopay_paid:
        return _("It already has invoice")
    address = credit.address
    address_json = {
        "company": address.company,
        "first_name": address.first_name,
        "last_name": address.last_name,
        "street": address.street,
        "city": address.city,
        "zip": address.zip,
        "phone": address.phone,
        "email": address.email,
        "org_reg_no": address.company_number,
        "vat_number": address.vat_number,
    }
    items = []
    #name,unit,count,price,vat
    items.append([
        config.pcp_invoices_item_desc,
        config.pcp_invoices_item_unit,
        credit.value - credit.bonus,
        (1 / float(config.credit_quotient)),
        0,
    ])
    invoice = {
        "key": config.pcp_invoices_api_key,
        "var_symbol": credit.user.parms.var_symbol,
        "address": address_json,
        "items":items,
        "bank_name": config.bank_name,
        "bank_account": config.bank_account,
        "send": True,
    }
    r = requests.post(config.pcp_invoices_api_url, data={"data": json.dumps(invoice)})
    credit.date_payed = datetime.now()
    credit.save()
    return "%s (%d)" % (r.text, r.status_code)
