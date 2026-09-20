import pytest
from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.core.management import call_command
from inventory.models import Product, Category
@pytest.fixture
def admin_user(db):
    call_command('setup_roles', verbosity=0)
    user = User.objects.create_user('tester', password='TestPassword!314')
    user.groups.add(Group.objects.get(name='Admin'))
    return user
@pytest.fixture
def staff_user(admin_user):
    user = User.objects.create_user('worker', password='TestPassword!314')
    user.groups.add(Group.objects.get(name='Staff'))
    return user
@pytest.fixture
def product(db):
    return Product.objects.create(name='Test product', sku='TEST-1', category=Category.objects.create(name='Test category'), cost_price=Decimal('12.35'), selling_price=Decimal('19.99'), minimum_stock_level=5)
