from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, F
from django.utils import timezone
from common.models import CatalogModel
from common.forms import validate_image

class Category(CatalogModel):
    description = models.TextField(blank=True)

class Product(CatalogModel):
    sku = models.CharField(max_length=80, unique=True)
    barcode = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.PROTECT, related_name='products', null=True, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    current_quantity = models.PositiveIntegerField(default=0, editable=False)
    minimum_stock_level = models.PositiveIntegerField(default=5)
    unit = models.CharField(max_length=30, default='pcs')
    image = models.ImageField(upload_to='products/', blank=True, validators=[validate_image])
    class Meta:
        ordering = ['name']
        constraints = [models.CheckConstraint(condition=Q(cost_price__gte=0) & Q(selling_price__gte=0), name='product_nonnegative_prices')]
        indexes = [models.Index(fields=['is_active', 'current_quantity'])]
        permissions = [('view_dashboard', 'Can view dashboard'), ('view_reports', 'Can view inventory reports'), ('stock_in', 'Can receive stock'), ('stock_out', 'Can issue stock')]
    def save(self, *args, **kwargs):
        # Ordinary saves must not overwrite a balance changed by a concurrent movement.
        if not self._state.adding and kwargs.get('update_fields') is None:
            kwargs['update_fields'] = [field.name for field in self._meta.concrete_fields if not field.primary_key and field.name != 'current_quantity']
        super().save(*args, **kwargs)

    @property
    def stock_status(self):
        if self.current_quantity == 0:
            return 'Out of stock'
        return 'Low stock' if self.current_quantity <= self.minimum_stock_level else 'In stock'
    @property
    def inventory_value(self):
        return self.current_quantity * self.cost_price

class StockTransaction(models.Model):
    class Type(models.TextChoices):
        IN = 'IN', 'Stock in'
        OUT = 'OUT', 'Stock out'
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='transactions')
    transaction_type = models.CharField(max_length=3, choices=Type.choices)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    quantity_before = models.PositiveIntegerField()
    quantity_after = models.PositiveIntegerField()
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.PROTECT, null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=100, blank=True, db_index=True)
    note = models.TextField(blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    transaction_date = models.DateField(default=timezone.localdate, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at', '-pk']
        constraints = [models.CheckConstraint(condition=Q(quantity__gt=0), name='movement_positive_quantity'), models.CheckConstraint(condition=(Q(transaction_type='IN', quantity_after=F('quantity_before') + F('quantity')) | Q(transaction_type='OUT', quantity_after=F('quantity_before') - F('quantity'))), name='movement_balanced')]
    def __str__(self):
        return f'{self.transaction_type} {self.quantity} × {self.product}'
