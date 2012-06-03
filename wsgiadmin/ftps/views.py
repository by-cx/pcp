import crypt

from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _, ugettext

from wsgiadmin.ftps.forms import FTPForm, FTPUpdateForm
from wsgiadmin.ftps.models import *
from wsgiadmin.service.forms import PassCheckForm, RostiFormHelper
from wsgiadmin.service.views import RostiListView, JsonResponse


class FTPListView(RostiListView):

    menu_active = 'ftps'
    template_name = 'ftps.html'
    delete_url_reverse = 'ftp_remove'

    def get_queryset(self, **kwargs):
        return Ftp.objects.filter(owner=self.user)


@login_required
def ftp_upsert(request, ftp_id=0):
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    try:
        ftp = Ftp.objects.get(pk=ftp_id)
    except Ftp.DoesNotExist:
        ftp = None

    if request.method == 'POST':
        if ftp:
            form = FTPUpdateForm(request.POST, user=u, instance=ftp)
        else:
            form = FTPForm(request.POST, user=u)

        if form.is_valid():
            iftp = form.save(commit=False)
            iftp.uid = u.parms.uid
            iftp.gid = u.parms.gid
            iftp.owner = u
            iftp.password = crypt.crypt(form.cleaned_data["password1"], iftp.owner.username)
            iftp.save()

            messages.add_message(request, messages.SUCCESS, _('FTP account has been %s') % _("changed") if ftp else _("added"))
            return HttpResponseRedirect(reverse("ftp_list"))
    else:
        if ftp:
            form = FTPUpdateForm(user=u, instance=ftp)
        else:
            form = FTPForm(user=u)

    helper = RostiFormHelper()
    helper.form_action = reverse("ftp_upsert", kwargs={'ftp_id': ftp_id})

    return render_to_response('universal.html',
            {
            "form": form,
            "form_helper": RostiFormHelper(),
            "title": _("FTP account"),
            "note": [_("* Username will be prefixed with `%s_`" % u.username)],
            "u": u,
            "superuser": superuser,
            "menu_active": "ftps",
            },
        context_instance=RequestContext(request)
    )


@login_required
def passwd_ftp(request, ftp_id):
    iftp = get_object_or_404(Ftp, id=ftp_id)
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if request.method == 'POST':
        form = PassCheckForm(request.POST)
        
        if form.is_valid():
            if iftp.owner != u:
                return HttpResponseForbidden(ugettext("Unable to edit chosen account"))

            iftp.password = crypt.crypt(form.cleaned_data["password1"], iftp.owner.username)
            iftp.save()
            #iftp.password = crypt.crypt(form.cleaned_data["password1"], iftp.owner.username)
            messages.add_message(request, messages.SUCCESS, _('Password has been changed'))
            return HttpResponseRedirect(reverse("ftp_list"))
    else:
        form = PassCheckForm()

    return render_to_response('universal.html',
            {
            "form": form,
            "form_helper": RostiFormHelper(),
            "title": _("Edit FTP account"),
            "submit": _("Save changes"),
            "action": reverse("ftp_passwd", kwargs={'ftp_id': ftp_id}),
            "u": u,
            "superuser": superuser,
            "menu_active": "ftps",
            },
        context_instance=RequestContext(request)
    )


@login_required
def remove_ftp(request):
    try:
        object_id = request.POST['object_id']

        try:
            ftp = Ftp.objects.get(id=object_id)
        except Ftp.DoesNotExist:
            raise Exception("redirect doesn't exist, obviously")
        else:
            ftp.delete()

        return JsonResponse("OK", {1: ugettext("FTP account was successfuly deleted")})
    except Exception, e:
        return JsonResponse("KO", {1: ugettext("Error during FTP account delete")})
