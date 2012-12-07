from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.storage.base import Message
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from wsgiadmin.clients.forms import AddressForm
from wsgiadmin.clients.models import Address
from wsgiadmin.service.views import RostiCreateView, RostiUpdateView, RostiListView
from django.utils.translation import ugettext_lazy as _


@login_required
def delete_address(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden(_("Permission error"))
    user = request.session.get('switched_user', request.user)

    address = get_object_or_404(user.address_set.filter(removed=False), id=pk)
    if user.address_set.filter(removed=False).count() <= 1:
        messages.add_message(request, messages.ERROR, _("You can't delete last address"))
        return HttpResponseRedirect(reverse("address_list"))

    if address.default:
        address.removed = True
        address.save()
        new_default_address = user.address_set.filter(removed=False)[0]
        new_default_address.default = True
        new_default_address.save()
    else:
        address.removed = True
        address.save()
    messages.add_message(request, messages.ERROR, _("Address deleted"))

    return HttpResponseRedirect(reverse("address_list"))


class AddressCreate(RostiCreateView):
    form_class = AddressForm
    template_name = "universal.html"
    menu_active = "settings"
    success_url = reverse_lazy("address_list")

    def form_valid(self, form):
        value = super(AddressCreate, self).form_valid(form)
        self.object.user = self.user
        if self.object.default:
            for address in self.user.address_set.filter(default=True).filter(removed=False):
                address.default = False
                address.save()
            self.object.default = True
            self.user.email = form.cleaned_data.get("email")
            self.user.save()
        elif not self.user.address_set.count():
            self.object.default = True
            self.user.email = form.cleaned_data.get("email")
            self.user.save()
        self.object.save()

        return value


class AddressUpdate(RostiUpdateView):
    form_class = AddressForm
    model = Address
    template_name = "universal.html"
    menu_active = "settings"
    success_url = reverse_lazy("address_list")

    def form_valid(self, form):
        value = super(AddressUpdate, self).form_valid(form)
        if self.object.default:
            for address in self.user.address_set.filter(default=True).filter(removed=False):
                address.default = False
                address.save()
            self.object.default = True
            self.user.email = form.cleaned_data.get("email")
            self.user.save()
            self.object.save()

        if not self.user.address_set.filter(default=True).filter(removed=False):
            new_default_address = self.user.address_set.filter(removed=False)[0]
            new_default_address.default = True
            new_default_address.save()
            self.user.email = new_default_address.email
            self.user.save()
            messages.add_message(self.request, messages.INFO, _("Address %s chose as default" % new_default_address.name))

        return value


class AddressList(RostiListView):
    model = Address
    template_name = "addresses.html"
    menu_active = "settings"

    def get_queryset(self):
        queryset = super(AddressList, self).get_queryset()
        queryset = queryset.filter(user=self.user, removed=False)
        return queryset
