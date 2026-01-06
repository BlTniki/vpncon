import pytest
from decimal import Decimal
from vpncon.db import auto_transaction
from vpncon.subscriptions.service import SubscriptionServiceCRUD
from vpncon.subscriptions.model import Subscription, Role
from vpncon.exceptions import EntityAlreadyExistsException, EntityNotExistsException

@pytest.fixture
def service():
    return SubscriptionServiceCRUD()

@auto_transaction(always_rollback=True)
def test_create_subscription_success(service):
    service.create_subscription(subscription_id=1, price_in_rub=Decimal('100.00'), allowed_peers=5, period='P1M', role='ACTIVATED_USER')
    subscription = service.get_subscription(1)
    assert subscription is not None
    assert subscription.id == 1
    assert subscription.price_in_rub == Decimal('100.00')
    assert subscription.allowed_peers == 5
    assert subscription.period == 'P1M'
    assert subscription.role == Role.ACTIVATED_USER

@auto_transaction(always_rollback=True)
def test_create_subscription_conflict(service):
    service.create_subscription(2, Decimal('200.00'), 10, 'P2M', 'ADMIN')
    with pytest.raises(EntityAlreadyExistsException):
        service.create_subscription(2, Decimal('250.00'), 15, 'P3M', 'ADMIN')

@auto_transaction(always_rollback=True)
def test_get_subscription_not_exists(service):
    assert service.get_subscription(999999) is None

@auto_transaction(always_rollback=True)
def test_get_subscriptions_by_role(service):
    service.create_subscription(3, Decimal('150.00'), 7, 'P1M', 'ACTIVATED_USER')
    service.create_subscription(4, Decimal('300.00'), 20, 'P3M', 'ADMIN')
    service.create_subscription(5, Decimal('120.00'), 6, 'P1M', 'ACTIVATED_USER')

    activated_subs = service.get_subscriptions_by_role('ACTIVATED_USER')
    admin_subs = service.get_subscriptions_by_role('ADMIN')

    assert len(activated_subs) == 2
    assert len(admin_subs) == 1
    assert all(sub.role == Role.ACTIVATED_USER for sub in activated_subs)
    assert all(sub.role == Role.ADMIN for sub in admin_subs)

@auto_transaction(always_rollback=True)
def test_update_subscription_success(service):
    service.create_subscription(6, Decimal('180.00'), 8, 'P2M', 'ACTIVATED_USER')

    service.update_subscription(6, Decimal('200.00'), 10, 'P3M', 'ADMIN')
    subscription = service.get_subscription(6)

    assert subscription.price_in_rub == Decimal('200.00')
    assert subscription.allowed_peers == 10
    assert subscription.period == 'P3M'
    assert subscription.role == Role.ADMIN

@auto_transaction(always_rollback=True)
def test_update_subscription_not_exists(service):
    with pytest.raises(EntityNotExistsException):
        service.update_subscription(500000, Decimal('100.00'), 5, 'P1M', 'ACTIVATED_USER')

@auto_transaction(always_rollback=True)
def test_delete_subscription_success(service):
    service.create_subscription(7, Decimal('250.00'), 12, 'P6M', 'ACTIVATED_USER')
    service.delete_subscription(7)
    assert service.get_subscription(7) is None

@auto_transaction(always_rollback=True)
def test_delete_subscription_not_exists(service):
    with pytest.raises(EntityNotExistsException):
        service.delete_subscription(123456)