from django.forms.models import ModelForm
from wsgiadmin.invoices.models import invoice, item

class InvoiceForm(ModelForm):
    class Meta:
        model = invoice
        exclude = ("byhand")


class ItemForm(ModelForm):
    class Meta:
        model = item
        exclude = ("invoice")
