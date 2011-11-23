from constance import config
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wsgiadmin.stats.models import Credit
from django.utils.translation import ugettext_lazy as _

class CreditView(TemplateView):
    template_name = "credit.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.session.get('switched_user', request.user)
        return super(CreditView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get("credit"):
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
