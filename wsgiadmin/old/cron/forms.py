from django.forms.models import ModelForm
from wsgiadmin.old.cron.models import Cron
from wsgiadmin.service.forms import RostiFormHelper

class FormCron(ModelForm):
    helper = RostiFormHelper()

    class Meta:
        model = Cron
        fields = ('time', 'script')
