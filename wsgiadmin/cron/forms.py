from django.forms.models import ModelForm
from wsgiadmin.cron.models import Cron

class FormCron(ModelForm):
    class Meta:
        model = Cron
        fields = ('time', 'script')