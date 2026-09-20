from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
class Command(BaseCommand):
    help = 'Create or restore the standard Admin, Manager and Staff roles.'
    def handle(self, *args, **options):
        all_permissions = Permission.objects.all()
        for name in ['Admin', 'Manager', 'Staff']:
            group, _ = Group.objects.get_or_create(name=name)
            if name == 'Admin':
                permissions = all_permissions
            elif name == 'Manager':
                permissions = all_permissions.filter(content_type__app_label__in=['inventory', 'suppliers']).exclude(codename__in=['add_stocktransaction', 'change_stocktransaction', 'delete_stocktransaction'])
            else:
                permissions = all_permissions.filter(codename__in=['view_product', 'view_category', 'view_supplier', 'view_stocktransaction', 'stock_in', 'stock_out'], content_type__app_label__in=['inventory', 'suppliers'])
            group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS('Admin, Manager and Staff roles configured.'))
