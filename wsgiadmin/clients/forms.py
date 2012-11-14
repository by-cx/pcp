from django.contrib.auth.models import User
from django.forms.models import ModelForm
from wsgiadmin.clients.models import Parms, Address
from wsgiadmin.service.forms import RostiFormHelper


class ParmsForm(ModelForm):
    class Meta:
        model = Parms
        fields = ("home", "note", "discount", "fee", "enable")


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ("username", )

class AddressForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = RostiFormHelper()
        super(AddressForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Address
        exclude = ("user", )
