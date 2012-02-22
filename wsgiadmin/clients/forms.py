from django.contrib.auth.models import User
from django.forms.models import ModelForm
from wsgiadmin.clients.models import Parms


class ParmsForm(ModelForm):
    class Meta:
        model = Parms
        fields = ("home", "note", "discount", "fee", "enable")


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ("username", )
