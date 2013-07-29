from django.conf import settings
from django.forms.models import ModelForm
from django import forms
from wsgiadmin.apps.models import App, Db
from django.utils.translation import ugettext_lazy as _
import re
from wsgiadmin.core.utils import server_chooser
from wsgiadmin.service.forms import RostiFormHelper


class DbFormPasswd(ModelForm):
    helper = RostiFormHelper()

    class Meta:
        model = Db
        fields = ["password", "comment"]
        widgets = {
            'password': forms.PasswordInput,
        }


class DbForm(ModelForm):
    helper = RostiFormHelper()

    def __init__(self, *args, **kwargs):
        super(DbForm, self).__init__(*args, **kwargs)
        self.fields["db_type"].help_text = _("PostgreSQL database has public scheme as default. Make sure, you create your own. Otherwise everybody can see your tables/views/.. (not data, just structure).")

    class Meta:
        model = Db
        fields = ["db_type", "password", "comment", "pg_postgis"]
        widgets = {
            'password': forms.PasswordInput,
        }


class AppForm(ModelForm):
    helper = RostiFormHelper()

    class Meta:
        model = App
        fields = ("name", "domains", "core_server")

    def __init__(self, *args, **kwargs):
        super(AppForm, self).__init__(*args, **kwargs)
        self.fields["domains"].help_text = _("On these domains your app will listen. There is no relation to DNS. Write your domains separated by spaces. For example: mydomain.cz www.mydomain.cz")

    def clean_domains(self):
        domains = self.cleaned_data["domains"].split()
        used_domains = []
        for x in [app.domains_list for app in App.objects.all()]:
            used_domains += x
        for domain in domains:
            if not re.match("^[0-9a-z_\.\-]*$", domain):
                raise forms.ValidationError(_("Each domain has to be in this format: ^[0-9a-z_\.\-]*$"))
            if domain in used_domains:
                raise forms.ValidationError(_("One of your domain is already used. (%s)" % domain))
        return self.cleaned_data["domains"]

    def clean_name(self):
        if not re.match("^[0-9a-zA-Z_\ \.\-]*$", self.cleaned_data["name"]):
            raise forms.ValidationError(_("App name has to be in this format: ^[0-9a-zA-Z_\ \.\-]*$"))
        if self.user.app_set.filter(name=self.cleaned_data["name"]):
            raise forms.ValidationError(_("This name is already used"))
        return self.cleaned_data["name"]


class AppParametersForm(forms.Form):
    helper = RostiFormHelper()
    this_app = None

    domains = forms.CharField(
        max_length=1024,
        required=False,
        label=_("Domains"),
        help_text=_("There is no relation to DNS or Domains menu. Write your domains separated by spaces.")
    )
    password = forms.CharField(
        max_length=128,
        required=False,
        label=_("Password"),
        widget=forms.PasswordInput,
        help_text=_("For SSH/SFTP/FTP")
    )

    def clean_domains(self):
        domains = self.cleaned_data["domains"].split()
        used_domains = []
        for x in [app.domains_list for app in App.objects.all() if not self.this_app or self.this_app.id != app.id]:
            used_domains += x
        for domain in domains:
            if not re.match("^[0-9a-z_\.\-\*]*$", domain):
                raise forms.ValidationError(_("Each domain has to be in this format: ^[0-9a-z_\.\-]*$"))
            if domain in used_domains:
                raise forms.ValidationError(_("One of your domain is already used. (%s)" % domain))

        return self.cleaned_data["domains"]



class AppStaticForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppStaticForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True

    flag_index = forms.BooleanField(
        label=_("Indexing"),
        help_text=_("Turn on/off indexing of your document root"),
        required=False,
    )


class AppPHPForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppPHPForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True

    flag_index = forms.BooleanField(
        label=_("Indexing"),
        help_text=_("Turn on/off indexing of your document root"),
        required=False,
    )
    memory_limit = forms.ChoiceField(label=_("memory_limit"), choices=[(x, x) for x in ("32M", "64M", "128M", "256M")])
    post_max_size = forms.ChoiceField(label=_("post_max_size"), choices=[(x, x) for x in ("32M", "64M", "128M", "256M", "512M")])
    upload_max_filesize = forms.ChoiceField(label=_("upload_max_filesize"), choices=[(x, x) for x in ("32M", "64M", "128M", "256M", "512M")])
    max_file_uploads = forms.ChoiceField(label=_("max_file_uploads"), choices=[(x, "%d" % x) for x in range(5,51,5)])
    max_execution_time = forms.ChoiceField(label=_("max_execution_time"), choices=[(x, "%ds" % x) for x in range(20,121,20)])
    allow_url_fopen = forms.BooleanField(label=_("allow_url_fopen"), initial=False, required=False)
    display_errors = forms.BooleanField(label=_("display_errors"), initial=True, required=False)


class AppPythonForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppPythonForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True

    script = forms.CharField(
        label=_("WSGI Script"),
        max_length=8192,
        widget=forms.Textarea(attrs={"class": "textarea-code"}),
        help_text=_("Write python code, which create WSGI handler of your app.")
    )
    python = forms.ChoiceField(
        label=_("Python version"),
        required=True,
        choices=[]
    )
    procs = forms.ChoiceField(
        label=_("Processes"),
        required=True,
        choices=[(x, x) for x in range(1,10)]
    )
    virtualenv = forms.CharField(
        label=_("Virtualenv"),
        max_length=4096,
        required=False,
        widget=forms.Textarea(attrs={"class": "textarea-code"}),
        help_text=_("List of requirements. One package per one line. Like requirements.txt file.")
    )
    static_maps = forms.CharField(
        label=_("Static maps"),
        required=False,
        widget=forms.Textarea(attrs={"class": "textarea-code"}),
        help_text=_("Consider your app as root. One pair <em>/url/ /path/</em> per line.")
    )
    memory = forms.ChoiceField(label=_("Max memory"), choices=(("256", "256 MB"), ("380", "380 MB"), ("512", "512 MB")))


class AppNativeForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppNativeForm, self).__init__(*args, **kwargs)
        self.fields["domains"] = None

    command = forms.CharField(
        label=_("Command"),
        max_length=1024,
    )

class AppProxyForm(AppParametersForm):
    def __init__(self, *args, **kwargs):
        super(AppProxyForm, self).__init__(*args, **kwargs)
        self.fields["domains"].required = True
        self.fields["domains"].help_text = "There is no relation to DNS or Domains menu."
