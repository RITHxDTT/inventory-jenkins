from django import forms
from common.forms import StyledFormMixin
from .models import Supplier
class SupplierForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ['created_at', 'updated_at']
