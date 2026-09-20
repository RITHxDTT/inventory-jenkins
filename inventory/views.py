from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import render, redirect
from common.views import catalog_views, page_context
from .models import Product, Category, StockTransaction
from .forms import ProductForm, CategoryForm, StockForm
from .filters import ProductFilter, CategoryFilter, TransactionFilter
from .services import move_stock
product_list, product_detail, product_edit, product_archive = catalog_views(Product, ProductForm, ProductFilter, 'products')
category_list, category_detail, category_edit, category_archive = catalog_views(Category, CategoryForm, CategoryFilter, 'categories')
@login_required
def stock(request, direction):
    if direction not in ('IN', 'OUT'):
        raise PermissionDenied
    if not request.user.has_perm('inventory.stock_in' if direction == 'IN' else 'inventory.stock_out'):
        raise PermissionDenied
    form = StockForm(request.POST or None, direction=direction, initial={'product': request.GET.get('product')})
    if request.method == 'POST' and form.is_valid():
        try:
            move_stock(**form.cleaned_data, transaction_type=direction, user=request.user)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, 'Stock added successfully.' if direction == 'IN' else 'Stock removed successfully.')
            return redirect('products-detail', pk=form.cleaned_data['product'].pk)
    return render(request, 'form.html', {'title': 'Receive stock' if direction == 'IN' else 'Issue stock', 'subtitle': 'Every movement is recorded with your name and the before / after balance.', 'form': form, 'cancel_url': 'products-list'})
@login_required
@permission_required('inventory.view_stocktransaction', raise_exception=True)
def transactions(request):
    f = TransactionFilter(request.GET, queryset=StockTransaction.objects.select_related('product', 'performed_by', 'supplier'))
    return render(request, 'transactions.html', dict(title='Transaction history', filter=f, **page_context(request, f.qs)))
