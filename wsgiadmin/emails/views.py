import crypt
from datetime import date

from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _, ugettext

from wsgiadmin.emails.forms import FormEmail, FormRedirect
from wsgiadmin.emails.models import Email, EmailRedirect
from wsgiadmin.requests.request import EMailRequest
from wsgiadmin.service.forms import PassCheckModelForm, RostiFormHelper
from wsgiadmin.service.views import JsonResponse, RostiListView
from constance import config


class MailboxListView(RostiListView):

    menu_active = 'emails'
    template_name = 'boxes.html'
    delete_url_reverse = 'mailbox_remove'

    def get_queryset(self, **kwargs):
        return Email.objects.filter(domain__in=self.user.domain_set.all(), remove=False)


@login_required
def addBox(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    domains = [(x.name, x.name) for x in u.domain_set.filter(mail=True)]

    if request.method == 'POST':
        form = FormEmail(request.POST)
        form.fields["xdomain"].choices = domains

        if form.is_valid():
            form.cleaned_data["xdomain"] = get_object_or_404(u.domain_set, name=
            form.cleaned_data["xdomain"])
            email = form.save(commit=False)
            email.login = form.cleaned_data["login"]
            email.domain = form.cleaned_data["xdomain"]
            email.pub_date = date.today()
            email.password = crypt.crypt(form.cleaned_data["password1"],
                                         form.cleaned_data["login"])
            email.uid = config.email_uid
            email.gid = config.email_gid
            email.save()

            er = EMailRequest(u, u.parms.mail_machine)
            er.create_mailbox(email)

            messages.add_message(request, messages.INFO, _('Box will be created in few minutes'))
            return HttpResponseRedirect(reverse("mailbox_list"))
    else:
        form = FormEmail()
        form.fields["xdomain"].choices = domains

    helper = RostiFormHelper()

    return render_to_response('universal.html',
            {
            "form": form,
            "form_helper": helper,
            "title": _("New e-mail"),
            "submit": _("Create box"),
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
        context_instance=RequestContext(request)
    )


@login_required
def mailbox_remove(request):
    try:
        object_id = request.POST['object_id']
        u = request.session.get('switched_user', request.user)

        try:
            mail = Email.objects.get(domain__in=u.domain_set.all(), id=object_id)
        except EmailRedirect.DoesNotExist:
            raise Exception("redirect doesn't exist, obviously")
        else:
            mail.remove = True
            mail.save()

            er = EMailRequest(u, u.parms.mail_machine)
            er.remove_mailbox(mail)

        return JsonResponse("OK", {1: ugettext("Mailbox was successfuly deleted")})
    except Exception, e:
        return JsonResponse("KO", {1: ugettext("Error during mailbox delete")})


@login_required
def changePasswdBox(request, eid):
    eid = int(eid)
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    try:
        e = Email.objects.get(domain__in=u.domain_set.all(), id=eid)
    except Email.DoesNotExist:
        e = None

    if request.method == 'POST':
        form = PassCheckModelForm(request.POST, instance=e)
        if form.is_valid():
            email = form.save(commit=False)
            email.password = crypt.crypt(form.cleaned_data["password1"], email.login)
            email.save()
            messages.add_message(request, messages.SUCCESS, _('Password has been changed'))
            return HttpResponseRedirect(reverse("mailbox_list"))
    else:
        form = PassCheckModelForm(instance=e)

    helper = RostiFormHelper()
    helper.form_action = reverse("wsgiadmin.emails.views.changePasswdBox", args=[e.id])

    return render_to_response('universal.html',
            {
            "form": form,
            "form_helper": helper,
            "title": _("Change password for e-mail box"),
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
        context_instance=RequestContext(request)
    )


class EmailAliasListView(RostiListView):

    menu_active = 'emails'
    template_name = 'redirects.html'
    delete_url_reverse = 'alias_remove'

    def get_queryset(self, **kwargs):
        return EmailRedirect.objects.filter(domain__in=self.user.domain_set.all())


@login_required
def alias_remove(request):
    try:
        object_id = request.POST['object_id']
        u = request.session.get('switched_user', request.user)

        try:
            r = EmailRedirect.objects.get(id=object_id, domain__owner=u)
        except EmailRedirect.DoesNotExist:
            raise Exception("redirect doesn't exist, obviously")
        else:
            r.delete()

        return JsonResponse("OK", {1: ugettext("Email alias was successfuly deleted")})
    except Exception, e:
        return JsonResponse("KO", {1: ugettext("Error during alias delete")})


@login_required
def changeRedirect(request, rid):
    u = request.session.get('switched_user', request.user)
    superuser = request.user
    rid = int(rid)

    r = get_object_or_404(EmailRedirect, id=rid)
    if r.domain.owner != u:
        return HttpResponseForbidden(ugettext("Forbidden operation"))

    domains = [(x.name, x.name) for x in u.domain_set.filter(mail=True)]
    if request.method == 'POST':
        form = FormRedirect(request.POST, instance=r)
        form.fields["_domain"].choices = domains
        if form.is_valid():
            fredirect = form.save(commit=False)
            fredirect.domain = get_object_or_404(u.domain_set, name=form.cleaned_data["_domain"])
            fredirect.save()
            messages.add_message(request, messages.SUCCESS, _('Redirect has been changed'))
            return HttpResponseRedirect(reverse("redirect_list"))
    else:
        form = FormRedirect(instance=r)
        form.fields["_domain"].choices = domains

    helper = RostiFormHelper()
    helper.form_action = reverse("wsgiadmin.emails.views.changeRedirect", args=[rid])

    return render_to_response('universal.html',
            {
            "form": form,
            "form_helper": helper,
            "title": _("Modify email alias"),
            "submit": _("Save changes"),
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
        context_instance=RequestContext(request)
    )

@login_required
def addRedirect(request):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    domains = [(x.name, x.name) for x in u.domain_set.filter(mail=True)]
    if request.method == 'POST':
        form = FormRedirect(request.POST)
        form.fields["_domain"].choices = domains
        if form.is_valid():
            redirect = form.save(commit=False)
            redirect.alias = form.cleaned_data["alias"]
            redirect.domain = get_object_or_404(u.domain_set, name=form.cleaned_data["_domain"])
            redirect.pub_date = date.today()
            redirect.save()

            messages.add_message(request, messages.SUCCESS, _('Redirect has been added'))
            return HttpResponseRedirect(reverse("redirect_list"))
    else:
        form = FormRedirect()
        form.fields["_domain"].choices = domains

    helper = RostiFormHelper()
    helper.form_action = reverse("add_redirect")

    return render_to_response('universal.html',
            {
            "form": form,
            "form_helper": helper,
            "title": _("Add email redirect"),
            "submit": _("Add redirect"),
            "u": u,
            "superuser": superuser,
            "menu_active": "emails",
            },
        context_instance=RequestContext(request)
    )
