from django.contrib import admin
from common.admin import HistoryAdmin
from .models import AuditLog
@admin.register(AuditLog)
class AuditLogAdmin(HistoryAdmin):
    list_display = ['timestamp', 'user', 'action', 'object_type', 'object_id']
    list_filter = ['action', 'object_type']
    search_fields = ['description', 'user__username']
