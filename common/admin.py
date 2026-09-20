from django.contrib import admin
from audit.services import log_action
class LoggedAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        log_action(request.user, 'Admin updated' if change else 'Admin created', obj)
    def has_delete_permission(self, request, obj=None):
        return False
class HistoryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
