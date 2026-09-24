from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone
from audit.services import log_action
from .models import Product, StockTransaction


@transaction.atomic
def move_stock(*, product, quantity, transaction_type, user, supplier=None, reason='', reference_number='', note='',
               transaction_date=None):
    if transaction_type not in StockTransaction.Type.values:
        raise ValidationError('Invalid stock movement type.')
    permission = 'inventory.stock_in' if transaction_type == 'IN' else 'inventory.stock_out'
    if not user.is_active or not user.has_perm(permission):
        raise PermissionDenied
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValidationError('Quantity must be a positive whole number.')
    product = Product.objects.select_for_update().get(pk=product.pk)
    if not product.is_active:
        raise ValidationError('Archived products cannot receive stock movements.')
    if transaction_type == 'OUT' and not reason.strip():
        raise ValidationError('Please give a reason for stock out.')
    if supplier and not supplier.is_active:
        raise ValidationError('Choose an active supplier.')
    if transaction_type == 'OUT' and quantity > product.current_quantity:
        raise ValidationError(f'Insufficient stock. Only {product.current_quantity} {product.unit} available.')
    before = product.current_quantity
    product.current_quantity += quantity if transaction_type == 'IN' else -quantity
    product.save(update_fields=['current_quantity', 'updated_at'])
    movement = StockTransaction.objects.create(product=product, transaction_type=transaction_type, quantity=quantity,
                                               quantity_before=before, quantity_after=product.current_quantity,
                                               supplier=supplier if transaction_type == 'IN' else None, reason=reason,
                                               reference_number=reference_number, note=note, performed_by=user,
                                               transaction_date=transaction_date or timezone.localdate())
    log_action(user, f'Stock {transaction_type}', movement, f'{product.sku}: {before} → {product.current_quantity}')
    return movement
