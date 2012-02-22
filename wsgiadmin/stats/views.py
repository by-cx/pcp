from datetime import date, timedelta
from constance import config
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Min, Sum
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from jsonrpc.proxy import ServiceProxy
from wsgiadmin.stats.models import Credit, Record
from django.utils.translation import ugettext_lazy as _

class CreditView(TemplateView):
    template_name = "credit.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(CreditView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get("credit"):
            if settings.JSONRPC_URL:
                items = [{
                    "description": config.invoice_desc,
                    "count": float(request.POST.get("credit")),
                    "price": 1 / float(config.credit_currency.split(",")[0]), #TODO:change it to multicurrency
                    "tax": config.tax,
                }]

                proxy = ServiceProxy(settings.JSONRPC_URL)
                #TODO:what to do with exception?
                print proxy.add_invoice(
                    settings.JSONRPC_USERNAME,
                    settings.JSONRPC_PASSWORD,
                    self.user.parms.address_id,
                    items
                )

            self.user.parms.add_credit(float(request.POST.get("credit")))
            messages.add_message(request, messages.SUCCESS, _('Credit has been added on your account'))
            messages.add_message(request, messages.INFO, _('Invoice is going to reach your e-mail in next 24 hours'))
        if request.POST.get("what_to_do"):
            self.user.parms.low_level_credits = request.POST.get("what_to_do")
            self.user.parms.save()
            messages.add_message(request, messages.SUCCESS, _('Low level behavior has been setted'))
        return HttpResponseRedirect(reverse("credit"))

    def get_context_data(self, **kwargs):
        context = super(CreditView, self).get_context_data(**kwargs)
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['menu_active'] = "dashboard"
        context['config'] = config
        context["for_month"] = self.user.parms.pay_total_day() * 30.0
        context["for_three_months"] = self.user.parms.pay_total_day() * 90
        context["for_six_months"] = self.user.parms.pay_total_day() * 180
        context["for_year"] = self.user.parms.pay_total_day() * 360
        context["for_month_cost"] = (self.user.parms.pay_total_day() * 30.0) / self.user.parms.one_credit_cost
        context["for_three_months_cost"] = (self.user.parms.pay_total_day() * 90) / self.user.parms.one_credit_cost
        context["for_six_months_cost"] = (self.user.parms.pay_total_day() * 180) / self.user.parms.one_credit_cost
        context["for_year_cost"] = (self.user.parms.pay_total_day() * 360) / self.user.parms.one_credit_cost
        return context

class StatsView(TemplateView):
    template_name = "bill.html"

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
                    month = 0
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

    def buyed_stats(self):
        return self.user.credit_set.order_by("date")

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)
        context["months"] = self.month_stats()
        context["days"] = self.day_stats()
        context["credits"] = self.buyed_stats()
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['menu_active'] = "dashboard"
        context['config'] = config
        return context
