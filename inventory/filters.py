import django_filters as df
from django import forms
from django.db.models import Q, F
from .models import Product, StockTransaction, Category
from suppliers.models import Supplier
from django.contrib.auth.models import User
class StyledFilter(df.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.form.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
class ProductFilter(StyledFilter):
    q = df.CharFilter(method='search', label='Search name / SKU')
    stock = df.ChoiceFilter(choices=[('low', 'Low stock'), ('out', 'Out of stock'), ('in', 'In stock')], method='stock_filter')
    price_min = df.NumberFilter(field_name='selling_price', lookup_expr='gte')
    price_max = df.NumberFilter(field_name='selling_price', lookup_expr='lte')
    created_after = df.DateFilter(field_name='created_at', lookup_expr='date__gte', widget=forms.DateInput(attrs={'type': 'date'}))
    created_before = df.DateFilter(field_name='created_at', lookup_expr='date__lte', widget=forms.DateInput(attrs={'type': 'date'}))
    ordering = df.OrderingFilter(fields=['name', 'sku', 'current_quantity', 'selling_price', 'created_at'])
    class Meta:
        model = Product
        fields = ['q', 'category', 'supplier', 'stock', 'is_active']
    def search(self, qs, name, value):
        return qs.filter(Q(name__icontains=value) | Q(sku__icontains=value))
    def stock_filter(self, qs, name, value):
        if value == 'out': return qs.filter(current_quantity=0)
        if value == 'low': return qs.filter(current_quantity__gt=0, current_quantity__lte=F('minimum_stock_level'))
        return qs.filter(current_quantity__gt=F('minimum_stock_level'))
class TransactionFilter(StyledFilter):
    q = df.CharFilter(method='search', label='Search product / reference')
    date_from = df.DateFilter(field_name='transaction_date', lookup_expr='gte', widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = df.DateFilter(field_name='transaction_date', lookup_expr='lte', widget=forms.DateInput(attrs={'type': 'date'}))
    ordering = df.OrderingFilter(fields=['transaction_date', 'created_at', 'quantity'])
    class Meta:
        model = StockTransaction
        fields = ['q', 'product', 'transaction_type', 'performed_by']
    def search(self, qs, name, value):
        return qs.filter(Q(product__name__icontains=value) | Q(product__sku__icontains=value) | Q(reference_number__icontains=value))
class SupplierFilter(StyledFilter):
    name = df.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Supplier
        fields = ['name', 'is_active']
class CategoryFilter(StyledFilter):
    name = df.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Category
        fields = ['name', 'is_active']
class UserFilter(StyledFilter):
    q = df.CharFilter(method='search', label='Username / email')
    class Meta:
        model = User
        fields = ['q', 'groups', 'is_active']
    def search(self, qs, name, value):
        return qs.filter(Q(username__icontains=value) | Q(email__icontains=value)).distinct()
