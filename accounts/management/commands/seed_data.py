from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.utils import timezone
from inventory.models import Category, Product
from suppliers.models import Supplier
from inventory.services import move_stock
class Command(BaseCommand):
    help = 'Create development demo users and inventory (idempotent; DEBUG only).'
    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Demo data is only available with DEBUG=True.')
        call_command('setup_roles')
        for name, role in [('admin', 'Admin'), ('manager', 'Manager'), ('staff', 'Staff')]:
            user, created = User.objects.get_or_create(username=name, defaults={'email': f'{name}@example.com', 'first_name': name.title()})
            if created:
                user.set_password('DemoStock!2026')
                user.is_staff = name == 'admin'
                user.save()
                user.groups.add(Group.objects.get(name=role))
        actor = User.objects.get(username='admin')
        supplier, _ = Supplier.objects.get_or_create(name='Mekong Supply Co.', defaults={'contact_person': 'Sophea Chan', 'email': 'orders@example.com', 'phone': '+855 12 345 678', 'address': 'Phnom Penh, Cambodia'})
        data = [('Electronics', 'Wireless keyboard', 'EL-001', '24.50', 42), ('Electronics', 'USB-C hub', 'EL-002', '18.00', 6), ('Office essentials', 'A5 notebook', 'OF-001', '2.25', 120), ('Office essentials', 'Desk organizer', 'OF-002', '8.50', 0), ('Accessories', 'Laptop sleeve', 'AC-001', '12.00', 28), ('Accessories', 'Travel cable pouch', 'AC-002', '6.75', 3), ('Furniture', 'Adjustable desk lamp', 'FU-001', '29.00', 18), ('Furniture', 'Ergonomic chair', 'FU-002', '95.00', 9)]
        for index, (category, name, sku, cost, quantity) in enumerate(data):
            category, _ = Category.objects.get_or_create(name=category)
            product, created = Product.objects.get_or_create(sku=sku, defaults={'name': name, 'category': category, 'supplier': supplier, 'cost_price': Decimal(cost), 'selling_price': Decimal(cost) * Decimal('1.60'), 'minimum_stock_level': 8})
            if created and quantity:
                move_stock(product=product, quantity=quantity+5, transaction_type='IN', user=actor, supplier=supplier, reference_number=f'DEMO-IN-{sku}', transaction_date=timezone.localdate()-timedelta(days=index%7))
                move_stock(product=product, quantity=5, transaction_type='OUT', user=actor, reason='Demo customer order', reference_number=f'DEMO-OUT-{sku}', transaction_date=timezone.localdate()-timedelta(days=index%3))
        self.stdout.write(self.style.SUCCESS('Demo data ready. New accounts: admin / manager / staff. Password: DemoStock!2026'))
