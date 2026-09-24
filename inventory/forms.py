from django import forms
from django.utils import timezone
from common.forms import StyledFormMixin
from suppliers.models import Supplier
from .models import Product, Category


class ProductForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['current_quantity', 'created_at', 'updated_at']


class CategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']


class StockForm(StyledFormMixin, forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True))
    quantity = forms.IntegerField(min_value=1)
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.filter(is_active=True), required=False)
    reason = forms.CharField(max_length=200, required=False)
    reference_number = forms.CharField(max_length=100, required=False)
    transaction_date = forms.DateField(initial=timezone.localdate, widget=forms.DateInput(attrs={'type': 'date'}))
    note = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, direction='IN', **kwargs):
        super().__init__(*args, **kwargs)
        if direction == 'OUT':
            self.fields.pop('supplier')
            self.fields['reason'].required = True
        else:
            self.fields.pop('reason')
