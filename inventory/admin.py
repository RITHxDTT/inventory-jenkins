from django.contrib import admin
from common.admin import LoggedAdmin, HistoryAdmin
from .models import Product, Category, StockTransaction
@admin.register(Product)
class ProductAdmin(LoggedAdmin):
    list_display = ['name', 'sku', 'category', 'current_quantity', 'stock_status', 'is_active']
    list_filter = ['is_active', 'category', 'supplier']
    search_fields = ['name', 'sku']
    readonly_fields = ['current_quantity', 'created_at', 'updated_at']
@admin.register(Category)
class CategoryAdmin(LoggedAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']
@admin.register(StockTransaction)
class StockTransactionAdmin(HistoryAdmin):
    list_display = ['id', 'product', 'transaction_type', 'quantity', 'quantity_before', 'quantity_after', 'performed_by', 'transaction_date']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['product__sku', 'reference_number']
