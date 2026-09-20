from django.contrib import admin
from common.admin import LoggedAdmin
from .models import Supplier
@admin.register(Supplier)
class SupplierAdmin(LoggedAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'is_active']
    search_fields = ['name', 'email']
    list_filter = ['is_active']
