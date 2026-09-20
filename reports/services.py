from decimal import Decimal
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from inventory.models import Product

def inventory_value(queryset=None):
    qs = Product.objects.all() if queryset is None else queryset
    expression = ExpressionWrapper(F('current_quantity') * F('cost_price'), output_field=DecimalField(max_digits=24, decimal_places=2))
    return qs.aggregate(value=Sum(expression))['value'] or Decimal('0.00')
