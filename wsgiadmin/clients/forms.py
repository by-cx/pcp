from django.contrib.auth.models import User
from django.forms.models import ModelForm
from wsgiadmin.clients.models import Parms


class ParmsForm(ModelForm):
    class Meta:
        model = Parms
        exclude = ("address", "user", "home", "uid", "gid")


class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ("password", "is_staff", "is_superuser", "last_login", "date_joined", "groups", "user_permissions")
