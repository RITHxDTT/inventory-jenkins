from decimal import Decimal
from unittest.mock import patch
import pytest
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from inventory.models import Product, StockTransaction
from inventory.services import move_stock
from reports.services import inventory_value
pytestmark = pytest.mark.django_db

def move(product, admin_user, quantity, direction='IN'):
    return move_stock(product=product, user=admin_user, quantity=quantity, transaction_type=direction, reason='Order')

def test_stock_balances_and_reports(product, admin_user):
    assert product.stock_status == 'Out of stock'
    tx = move(product, admin_user, 12)
    assert (tx.quantity_before, tx.quantity_after) == (0, 12)
    product.refresh_from_db()
    assert product.stock_status == 'In stock'
    assert inventory_value() == Decimal('148.20')
    tx = move(product, admin_user, 7, 'OUT')
    product.refresh_from_db()
    assert (tx.quantity_before, tx.quantity_after) == (12, 5)
    assert product.stock_status == 'Low stock'
    move(product, admin_user, 5, 'OUT')
    product.refresh_from_db()
    assert product.stock_status == 'Out of stock'
    assert StockTransaction.objects.count() == 3

@pytest.mark.parametrize('quantity', [0, -1, 1.5, True])
def test_invalid_quantity(product, admin_user, quantity):
    with pytest.raises(ValidationError): move(product, admin_user, quantity)
    assert not StockTransaction.objects.exists()

def test_insufficient_stock(product, admin_user):
    move(product, admin_user, 5)
    with pytest.raises(ValidationError, match='Insufficient'): move(product, admin_user, 6, 'OUT')
    product.refresh_from_db()
    assert product.current_quantity == 5
    assert StockTransaction.objects.count() == 1

def test_atomic_rollback(product, admin_user):
    with patch('inventory.services.log_action', side_effect=RuntimeError('audit failed')):
        with pytest.raises(RuntimeError): move(product, admin_user, 10)
    product.refresh_from_db()
    assert product.current_quantity == 0
    assert not StockTransaction.objects.exists()

def test_unique_sku_and_nonnegative_prices(product):
    with pytest.raises(IntegrityError), transaction.atomic():
        Product.objects.create(name='Duplicate', sku=product.sku, category=product.category, cost_price=1, selling_price=2)
    product.cost_price = Decimal('-1')
    with pytest.raises(ValidationError): product.full_clean()

def test_archived_product_and_unauthorized_movement(product, admin_user, django_user_model):
    stranger = django_user_model.objects.create_user('stranger')
    with pytest.raises(PermissionDenied): move(product, stranger, 1)
    product.is_active = False; product.save()
    with pytest.raises(ValidationError, match='Archived'): move(product, admin_user, 1)

@pytest.mark.parametrize('url', ['/', '/products/', '/categories/', '/suppliers/', '/transactions/', '/reports/', '/accounts/users/', '/audit/', '/stock/IN/'])
def test_login_required(client, url):
    assert client.get(url).status_code == 302

@pytest.mark.parametrize('url', ['/accounts/users/', '/accounts/users/new/', '/accounts/roles/', '/audit/', '/reports/', '/products/new/'])
def test_staff_forbidden(client, staff_user, url):
    client.force_login(staff_user)
    assert client.get(url).status_code == 403

@pytest.mark.parametrize('url', ['/', '/products/', '/categories/', '/suppliers/', '/transactions/', '/stock/IN/', '/stock/OUT/', '/accounts/users/', '/accounts/users/new/', '/accounts/roles/', '/accounts/roles/new/', '/accounts/profile/', '/accounts/password_change/', '/audit/', '/reports/?kind=current', '/reports/?kind=low', '/reports/?kind=out', '/reports/?kind=in', '/reports/?kind=outgoing', '/reports/?kind=movement', '/reports/?kind=value'])
def test_pages_render(client, admin_user, product, url):
    client.force_login(admin_user)
    response = client.get(url)
    assert response.status_code == 200

def test_product_crud_ignores_quantity(client, admin_user, product):
    client.force_login(admin_user)
    data = {'name': 'New item', 'sku': 'NEW', 'category': product.category_id, 'cost_price': '10.00', 'selling_price': '15.00', 'minimum_stock_level': 4, 'unit': 'pcs', 'is_active': 'on', 'current_quantity': 999}
    assert client.post('/products/new/', data).status_code == 302
    created = Product.objects.get(sku='NEW')
    assert created.current_quantity == 0
    data['name'] = 'Updated'
    assert client.post(f'/products/{created.pk}/edit/', data).status_code == 302
    created.refresh_from_db()
    assert created.name == 'Updated' and created.current_quantity == 0
    assert client.get(f'/products/{created.pk}/').status_code == 200
    assert client.get(f'/products/{created.pk}/archive/').status_code == 200
    assert client.post(f'/products/{created.pk}/archive/').status_code == 302
    created.refresh_from_db()
    assert not created.is_active

def test_stock_form_and_filter(client, staff_user, product):
    client.force_login(staff_user)
    data = {'product': product.pk, 'quantity': 4, 'transaction_date': '2026-09-20', 'reason': 'Sale'}
    assert client.post('/stock/IN/', data).status_code == 302
    data['quantity'] = 5
    response = client.post('/stock/OUT/', data)
    assert response.status_code == 200 and b'Insufficient stock' in response.content
    assert client.get('/products/?stock=low').context['page_obj'].paginator.count == 1
    data['quantity'] = 4
    assert client.post('/stock/OUT/', data).status_code == 302
    assert client.get('/products/?stock=out').context['page_obj'].paginator.count == 1

def test_login_logout_and_password_reset(client, admin_user, mailoutbox):
    assert client.post('/accounts/login/', {'username': admin_user.username, 'password': 'TestPassword!314'}).status_code == 302
    assert client.get('/products/').status_code == 200
    assert client.get('/accounts/logout/').status_code == 405
    assert client.post('/accounts/logout/').status_code == 302
    admin_user.email = 'test@example.com'; admin_user.save()
    assert client.post('/accounts/password_reset/', {'email': admin_user.email}).status_code == 302
    assert len(mailoutbox) == 1

def test_catalog_and_user_forms(client, admin_user):
    from suppliers.models import Supplier
    from inventory.models import Category
    from django.contrib.auth.models import User
    client.force_login(admin_user)
    for slug, model in [('categories', Category), ('suppliers', Supplier)]:
        assert client.post(f'/{slug}/new/', {'name': 'Created', 'is_active': 'on'}).status_code == 302
        obj = model.objects.get(name='Created')
        assert client.get(f'/{slug}/{obj.pk}/').status_code == 200
        assert client.post(f'/{slug}/{obj.pk}/edit/', {'name': 'Updated', 'is_active': 'on'}).status_code == 302
        assert client.post(f'/{slug}/{obj.pk}/archive/').status_code == 302
        obj.refresh_from_db(); assert not obj.is_active
    assert client.post('/accounts/users/new/', {'username': 'newuser', 'password1': 'StrongPass!12345', 'password2': 'StrongPass!12345', 'is_active': 'on'}).status_code == 302
    user = User.objects.get(username='newuser')
    assert client.post(f'/accounts/users/{user.pk}/edit/', {'username': 'newuser'}).status_code == 302
    user.refresh_from_db(); assert not user.is_active

@pytest.mark.django_db(transaction=True)
def test_concurrent_stock_out_is_serialized(product, admin_user):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from django.db import close_old_connections
    from django.contrib.auth.models import User
    move(product, admin_user, 5)
    barrier = Barrier(2)
    def withdraw():
        close_old_connections()
        try:
            actor = User.objects.get(pk=admin_user.pk)
            item = Product.objects.get(pk=product.pk)
            barrier.wait(timeout=10)
            try:
                move(item, actor, 4, 'OUT')
                return 'ok'
            except ValidationError:
                return 'insufficient'
        finally:
            close_old_connections()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: withdraw(), range(2)))
    assert sorted(results) == ['insufficient', 'ok']
    product.refresh_from_db()
    assert product.current_quantity == 1
    assert StockTransaction.objects.filter(transaction_type='OUT').count() == 1

def test_stale_product_edit_does_not_overwrite_stock(product, admin_user):
    stale = Product.objects.get(pk=product.pk)
    move(product, admin_user, 10)
    stale.name = 'Edited while receiving stock'
    stale.save()
    product.refresh_from_db()
    assert product.current_quantity == 10
    assert product.name == stale.name
