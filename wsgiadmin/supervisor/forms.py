from django.forms.models import ModelForm
from wsgiadmin.supervisor.models import Program

class FormProgram(ModelForm):
    class Meta:
        model = Program