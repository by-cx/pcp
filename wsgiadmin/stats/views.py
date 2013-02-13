from datetime import date, timedelta
from constance import config
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Min, Sum
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from gopay4django.api import GoPay
from gopay4django.models import Payment
from wsgiadmin.clients.models import Address
from wsgiadmin.emails.models import Message
from wsgiadmin.service.views import RostiListView
from wsgiadmin.stats.models import Credit
from wsgiadmin.stats.tools import add_credit, payed
from gopay4django.signals import payment_changed
from django.dispatch import receiver


@receiver(payment_changed)
def payment_changed_callback(sender, **kwargs):
    payment = kwargs.get("payment")
    if payment.state == "PAID":
        credit = Credit.objects.get(id=int(payment.p4))
        payed(credit)


@login_required
def create_gopay_payment(request):
    user = request.session.get('switched_user', request.user)
    superuser = request.user
    credit = user.credit_set.get(id=request.GET.get("credit_id"))
    address = credit.address
    gopay = GoPay()
    url = gopay.create_payment(
        productName = settings.GOPAY_PRODUCT_NAME,
        totalPrice = credit.price,
        currency = "CZK",
        firstName = address.first_name,
        lastName = address.last_name,
        city = address.city,
        street = address.street,
        postalCode = address.zip,
        countryCode = "CZE",
        email = address.email,
        phoneNumber=int(address.phone.replace(" ", "")),
        p4="%d" % credit.id,
        name="%.2f credits for %s (credit_id=%d)" % (credit.price, user.username, credit.id),
    )
    credit.gopay_payment = Payment.objects.filter(p4=str(credit.id)).order_by("date").reverse()[0]
    credit.save()
    return HttpResponseRedirect(url)


class PaymentDone(TemplateView):
    template_name = "stats/payment_done.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(PaymentDone, self).dispatch(request, *args, **kwargs)

    def get_payment(self):
        return Payment.objects.get(uuid=self.request.GET.get("payment_uuid"))

    def get_credit(self):
        payment = self.get_payment()
        return self.user.credit_set.get(id=payment.p4)

    def get_payment_paid(self):
        payment = self.get_payment()
        if payment.state == "PAID":
            payed(self.get_credit())

    def get_context_data(self, **kwargs):
        context = super(PaymentDone, self).get_context_data(**kwargs)
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['menu_active'] = "dashboard"
        context['credit'] = self.get_credit()
        self.get_payment_paid()
        return context


class PaymentError(TemplateView):
    template_name = "stats/payment_error.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(PaymentError, self).dispatch(request, *args, **kwargs)

    def get_credit(self):
        payment = Payment.objects.get(uuid=self.request.GET.get("payment_uuid"))
        return self.user.credit_set.get(id=payment.p4)

    def get_context_data(self, **kwargs):
        context = super(PaymentError, self).get_context_data(**kwargs)
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['menu_active'] = "dashboard"
        context['credit'] = self.get_credit()
        return context


class CreditView(TemplateView):
    template_name = "stats/credit.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(CreditView, self).dispatch(request, *args, **kwargs)

    def add_credit(self, value):
        message = Message.objects.filter(purpose="add_credit")
        if message:
            message[0].send(config.email, {"user": self.user.username, "credit": value})

    def post(self, request, *args, **kwargs):
        right_format = False
        try:
            if request.POST.get("credit"):
                float(request.POST.get("credit"))
                right_format = True
        except UnicodeEncodeError:
            messages.add_message(request, messages.ERROR, _('Put number into form below.'))

        if right_format and float(request.POST.get("credit")) < 50:
            messages.add_message(request, messages.ERROR, _('Minimum value is 50 credits'))
        elif right_format:
            if request.POST.get("credit"):
                credit = add_credit(self.user, float(request.POST.get("credit")))
                message = Message.objects.filter(purpose="add_credit")
                if message:
                    message[0].send(config.email, {"user": self.user.username, "credit": float(request.POST.get("credit")), "bonus": float(request.POST.get("credit"))})
                messages.add_message(request, messages.SUCCESS, _('Credits will been added on your account after payment'))
                return HttpResponseRedirect(reverse("payment_info", kwargs={"pk": credit.id}))
        if request.POST.get("what_to_do"):
            self.user.parms.low_level_credits = request.POST.get("what_to_do")
            self.user.parms.save()
            messages.add_message(request, messages.SUCCESS, _('Low level behavior has been setted'))
        return HttpResponseRedirect(reverse("credit"))

    def get_credits(self):
        return self.user.credit_set.order_by("date")

    def get_context_data(self, **kwargs):
        context = super(CreditView, self).get_context_data(**kwargs)
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['menu_active'] = "dashboard"
        context['config'] = config
        context['credits'] = credits
        context['addresses_count'] = Address.objects.filter(user=self.user, removed=False).count()
        if self.user.parms.fee:
            context["for_month"] = self.user.parms.fee
            context["for_three_months"] = self.user.parms.fee * 3
            context["for_six_months"] = self.user.parms.fee * 6
            context["for_year"] = self.user.parms.fee * 12
            context["for_month_cost"] = self.user.parms.fee / self.user.parms.one_credit_cost
            context["for_three_months_cost"] = (self.user.parms.fee * 3) / self.user.parms.one_credit_cost
            context["for_six_months_cost"] = (self.user.parms.fee * 6) / self.user.parms.one_credit_cost
            context["for_year_cost"] = (self.user.parms.fee * 12) / self.user.parms.one_credit_cost
        else:
            context["for_month"] = self.user.parms.pay_total_day() * 30.0
            context["for_three_months"] = self.user.parms.pay_total_day() * 90
            context["for_six_months"] = self.user.parms.pay_total_day() * 180
            context["for_year"] = self.user.parms.pay_total_day() * 360
            context["for_month_cost"] = (self.user.parms.pay_total_day() * 30.0) / self.user.parms.one_credit_cost
            context["for_three_months_cost"] = (self.user.parms.pay_total_day() * 90) / self.user.parms.one_credit_cost
            context["for_six_months_cost"] = (self.user.parms.pay_total_day() * 180) / self.user.parms.one_credit_cost
            context["for_year_cost"] = (self.user.parms.pay_total_day() * 360) / self.user.parms.one_credit_cost
        return context


class PaymentsView(RostiListView):
    template_name = "stats/credits.html"
    model = Credit
    menu_active = "dashboard"

    def get_queryset(self):
        queryset = super(PaymentsView, self).get_queryset()
        if not self.user.is_superuser:
            queryset = queryset.filter(user=self.user)
        queryset = queryset.order_by("date").reverse()
        return queryset


class PaymentView(TemplateView):
    template_name = "stats/payment_infopage.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(PaymentView, self).dispatch(request, *args, **kwargs)

    def get_credit(self):
        if not self.user.is_superuser:
            return get_object_or_404(self.user.credit_set, id=self.kwargs.get("pk"))
        return get_object_or_404(Credit.objects, id=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context["credit"] = self.get_credit()
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['menu_active'] = "dashboard"
        context['config'] = config
        context['gopay'] = settings.GOPAY
        context['addresses'] = self.user.address_set.filter(removed=False)
        return context


@login_required
def change_address(request):
    user = request.session.get('switched_user', request.user)
    superuser = request.user

    credit = get_object_or_404(user.credit_set, id=request.POST.get("credit_id"))
    address = get_object_or_404(user.address_set.filter(removed=False), id=request.POST.get("address_id"))

    if credit and address:
        credit.address = address
        credit.save()
        messages.add_message(request, messages.SUCCESS, _("Address has been changed"))
    else:
        messages.add_message(request, messages.ERROR, _("Address hasn't been changed"))

    return HttpResponseRedirect(reverse("payment_info", kwargs={"pk": credit.pk}))


class StatsView(TemplateView):
    template_name = "stats/bill.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(StatsView, self).dispatch(request, *args, **kwargs)

    def month_stats(self):
        today = date.today()
        objs = self.user.record_set.aggregate(Min("date"))
        first_day = objs["date__min"] if objs else date.today()
        if not first_day:
            return []
        month = first_day.month
        year = first_day.year
        data = []
        while year <= today.year:
            while month <= today.month:
                res = self.user.record_set.filter(date__year=year, date__month=month).aggregate(Sum("cost"))
                if res:
                    data.append({"label": "%d/%d" % (month, year), "cost": res["cost__sum"]})
                else:
                    data.append({"label": "%d/%d" % (month, year), "cost": 0.0})
                if month == 12:
                    year += 1
                    month = 1
                    break
                month += 1
            year += 1
        return data

    def day_stats(self):
        records = self.user.record_set.filter(date__gte=date.today() - timedelta(14)).order_by("date").distinct().values("date")
        data = []
        for record in records.all():
            res = self.user.record_set.filter(date=record["date"]).aggregate(Sum("cost"))
            if res:
                data.append({"date": record["date"], "cost": res["cost__sum"]})
            else:
                data.append({"date": record["date"], "cost": 0.0})
        return data

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)
        context["months"] = self.month_stats()
        context["days"] = self.day_stats()
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['menu_active'] = "dashboard"
        context['config'] = config
        return context


@login_required
def send_invoice(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    if not superuser.is_superuser:
        return HttpResponseForbidden(_("Permission error"))

    credit = get_object_or_404(Credit, id=request.GET.get("credit_id"))
    msg = payed(credit)
    messages.add_message(request, messages.INFO, _('API call result: %s' % msg))
    return HttpResponseRedirect(reverse("payments_info"))
