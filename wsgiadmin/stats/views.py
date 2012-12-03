from datetime import date, timedelta, datetime
from constance import config
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Min, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.clients.models import Address
from wsgiadmin.emails.models import Message
from wsgiadmin.service.views import RostiListView
from wsgiadmin.stats.models import Credit
from wsgiadmin.stats.tools import add_credit


class CreditView(TemplateView):
    template_name = "credit.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(CreditView, self).dispatch(request, *args, **kwargs)

    def add_credit(self, value):
        message = Message.objects.filter(purpose="add_credit")
        if message:
            message[0].send(config.email, {"user": self.user.username, "credit": value})

    def post(self, request, *args, **kwargs):
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
        context['addresses_count'] = Address.objects.filter(user=self.user).count()
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
    template_name = "credits.html"
    model = Credit
    menu_active = "dashboard"

    def get_queryset(self):
        queryset = super(PaymentsView, self).get_queryset()
        queryset = queryset.filter(user=self.user).order_by("date")
        return queryset


class PaymentView(TemplateView):
    template_name = "payment_infopage.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(PaymentView, self).dispatch(request, *args, **kwargs)

    def get_credit(self):
        return get_object_or_404(self.user.credit_set, id=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context["credit"] = self.get_credit()
        context['u'] = self.user
        context['superuser'] = self.request.user
        context['menu_active'] = "dashboard"
        context['config'] = config
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
