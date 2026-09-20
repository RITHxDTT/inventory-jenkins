from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from common.admin import LoggedAdmin
from .models import Profile
@admin.register(Profile)
class ProfileAdmin(LoggedAdmin):
    list_display = ['user']
    search_fields = ['user__username']
admin.site.unregister(User)
@admin.register(User)
class SafeUserAdmin(UserAdmin):
    def has_delete_permission(self, request, obj=None): return False
