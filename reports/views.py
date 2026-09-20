from datetime import timedelta
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from django.utils import timezone
from common.views import page_context
from inventory.models import Product, Category, StockTransaction
from inventory.filters import ProductFilter, TransactionFilter
from suppliers.models import Supplier
from .services import inventory_value
@login_required
def dashboard(request):
    if not request.user.has_perm('inventory.view_dashboard'):
        return redirect('products-list')
    products = Product.objects.all()
    today = timezone.localdate()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    movement = StockTransaction.objects.filter(transaction_date__range=(days[0], today)).values('transaction_date', 'transaction_type').annotate(total=Sum('quantity'))
    totals = {(r['transaction_date'], r['transaction_type']): r['total'] for r in movement}
    categories = list(Category.objects.annotate(units=Sum('products__current_quantity')).values('name', 'units'))
    cards = [('Total products', products.count(), 'products-list', ''), ('Categories', Category.objects.count(), 'categories-list', ''), ('Suppliers', Supplier.objects.count(), 'suppliers-list', ''), ('Stock units', products.aggregate(n=Sum('current_quantity'))['n'] or 0, 'products-list', ''), ('Low stock', products.filter(current_quantity__gt=0, current_quantity__lte=F('minimum_stock_level')).count(), 'products-list', '?stock=low'), ('Out of stock', products.filter(current_quantity=0).count(), 'products-list', '?stock=out'), ('Inventory value', f'${inventory_value():,.2f}', 'reports', '?kind=value')]
    chart = {'labels': [d.strftime('%a %d') for d in days], 'incoming': [totals.get((d, 'IN'), 0) for d in days], 'outgoing': [totals.get((d, 'OUT'), 0) for d in days], 'categories': [c['name'] for c in categories], 'units': [c['units'] or 0 for c in categories]}
    return render(request, 'dashboard.html', {'title': 'Overview', 'cards': cards, 'chart': chart, 'recent': StockTransaction.objects.select_related('product', 'performed_by')[:8]})
@login_required
@permission_required('inventory.view_reports', raise_exception=True)
def reports(request):
    kind = request.GET.get('kind', 'current')
    kinds = [('current', 'Current inventory'), ('low', 'Low stock'), ('out', 'Out of stock'), ('in', 'Stock in'), ('outgoing', 'Stock out'), ('movement', 'Inventory movement'), ('value', 'Inventory value')]
    if kind not in dict(kinds): kind = 'current'
    is_movement = kind in ('in', 'outgoing', 'movement')
    if is_movement:
        qs = StockTransaction.objects.select_related('product', 'performed_by')
        if kind != 'movement': qs = qs.filter(transaction_type='IN' if kind == 'in' else 'OUT')
        f = TransactionFilter(request.GET, queryset=qs)
        summary = {'Stock in units': f.qs.filter(transaction_type='IN').aggregate(n=Sum('quantity'))['n'] or 0, 'Stock out units': f.qs.filter(transaction_type='OUT').aggregate(n=Sum('quantity'))['n'] or 0}
    else:
        qs = Product.objects.select_related('category', 'supplier')
        if kind == 'low': qs = qs.filter(current_quantity__gt=0, current_quantity__lte=F('minimum_stock_level'))
        if kind == 'out': qs = qs.filter(current_quantity=0)
        f = ProductFilter(request.GET, queryset=qs)
        summary = {'Products': f.qs.count(), 'Inventory value ($)': inventory_value(f.qs)}
    return render(request, 'reports.html', dict(title=dict(kinds)[kind], kind=kind, kinds=kinds, movement=is_movement, filter=f, summary=summary, **page_context(request, f.qs)))
