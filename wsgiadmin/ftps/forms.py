from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from wsgiadmin.apacheconf.tools import user_directories

from wsgiadmin.ftps.models import Ftp
from wsgiadmin.service.forms import PassCheckModelForm


class FTPUpdateForm(ModelForm):

    class Meta:
        model = Ftp
        fields = ('username', 'dir')
        widgets = {
            'dir': forms.Select,
            }

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(FTPUpdateForm, self).__init__(*args, **kwargs)

        user_dirs = user_directories(user=self.user, use_cache=True)
        dirs_choices = [("", _("Not selected"))] + [(x, x) for x in user_dirs]
        self.fields['dir'].widget.choices = dirs_choices
        if 'username' in self.initial:
            self.initial['username'] = self.initial['username'][len(self.user.username)+1:]


    def clean_username(self):
        out_value = "%s_%s" % (self.user.username, self.cleaned_data["username"])
        if Ftp.objects.filter(username=out_value).exclude(pk=self.instance.pk).count():
            raise forms.ValidationError(_("Chosen username already exists"))

        return out_value

    def clean_dir(self):
        if ".." in self.cleaned_data["dir"] or "~" in self.cleaned_data["dir"]:
            raise forms.ValidationError(_("This field hasn't to contain .. and ~"))
        return self.cleaned_data["dir"]


class FTPForm(PassCheckModelForm, FTPUpdateForm):
    class Meta:
        model = Ftp
        fields = ('username', 'dir', 'password1', 'password2')
        widgets = {
            'dir': forms.Select,
            }

    def clean(self):
        super(FTPForm, self).clean()
        super(FTPForm, self).clean_password1()
        self.cleaned_data['password1'] = self.cleaned_data['password1']
        return self.cleaned_data

    def clean_username(self):
        out_value = "%s_%s" % (self.user.username, self.cleaned_data["username"])
        if Ftp.objects.filter(username=out_value).count():
            raise forms.ValidationError(_("Chosen username already exists"))

        return out_value
