from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _

from wsgiadmin.emails.models import Email, EmailRedirect
from wsgiadmin.service.forms import PassCheckModelForm


class FormEmail(PassCheckModelForm):
    login = forms.CharField(label=_("Name"), help_text=_("Mailbox in name@domain format"))
    xdomain = forms.ChoiceField(label=_("Domain"), choices=[(11, 22)])

    class Meta:
        model = Email
        fields = ("login", "xdomain", "password1", "password2")

    def clean_login(self):
        if Email.objects.filter(remove=False, domain__name=self.data['xdomain'], login=self.cleaned_data["login"]).count():
            raise forms.ValidationError(_("Given username already exists"))

        return self.cleaned_data["login"]


class FormLogin(forms.Form):
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))


class FormRedirect(ModelForm):
    _domain = forms.ChoiceField(label=_("Domain"), choices=[(11, 22)])

    class Meta:
        model = EmailRedirect
        exclude = ("pub_date", "owner", "domain")
        fields = ('alias', '_domain', 'email')


    def clean_login(self):
        if Email.objects.filter(domain__name=self.data['domain'], login=self.cleaned_data["alias"]).count():
            raise forms.ValidationError(_("Given alias already exists"))

        return self.cleaned_data["alias"]
