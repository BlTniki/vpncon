import pytest
from decimal import Decimal
from vpncon.db import auto_transaction
from vpncon.user_subscriptions.service import UserSubscriptionServiceCRUD
from vpncon.users.service import UserServiceCRUD
from vpncon.subscriptions.service import SubscriptionServiceCRUD
from vpncon.user_subscriptions.model import UserSubscription
from vpncon.users.model import Role as UserRole
from vpncon.subscriptions.model import Role as SubscriptionRole
from vpncon.exceptions import EntityAlreadyExistsException, EntityNotExistsException

@pytest.fixture
def user_service():
    return UserServiceCRUD()

@pytest.fixture
def subscription_service():
    return SubscriptionServiceCRUD()

@pytest.fixture
def user_subscription_service():
    return UserSubscriptionServiceCRUD()

@auto_transaction(always_rollback=True)
def test_create_user_subscription_success(user_service, subscription_service, user_subscription_service):
    # Create user
    user_service.create_user(telegram_id=1, telegram_nick="nick1", role="ACTIVATED_USER")
    # Create subscription
    subscription_service.create_subscription(
        subscription_id=1,
        price_in_rub=Decimal("100.00"),
        allowed_peers=5,
        period="P1M",
        role="ACTIVATED_USER"
    )
    # Create user subscription
    user_subscription_service.create_user_subscription(
        telegram_id=1,
        subscription_id=1,
        expiry_date="2024-12-31"
    )
    # Get and assert
    user_sub = user_subscription_service.get_user_subscription(1)
    assert user_sub is not None
    assert user_sub.user.telegram_id == 1
    assert user_sub.user.telegram_nick == "nick1"
    assert user_sub.user.role == UserRole.ACTIVATED_USER
    assert user_sub.subscription.id == 1
    assert user_sub.subscription.price_in_rub == Decimal("100.00")
    assert user_sub.subscription.allowed_peers == 5
    assert user_sub.subscription.period == "P1M"
    assert user_sub.subscription.role == SubscriptionRole.ACTIVATED_USER
    assert user_sub.expiry_date == "2024-12-31"

@auto_transaction(always_rollback=True)
def test_create_user_subscription_conflict(user_service, subscription_service, user_subscription_service):
    # Create user and subscription
    user_service.create_user(2, "nick2", "ACTIVATED_USER")
    subscription_service.create_subscription(2, Decimal("200.00"), 10, "P1Y", "ACTIVATED_USER")
    # Create user subscription
    user_subscription_service.create_user_subscription(2, 2, "2025-12-31")
    # Try to create again
    with pytest.raises(EntityAlreadyExistsException):
        user_subscription_service.create_user_subscription(2, 2, "2026-12-31")

@auto_transaction(always_rollback=True)
def test_get_user_subscription_not_exists(user_subscription_service):
    assert user_subscription_service.get_user_subscription(999999) is None

@auto_transaction(always_rollback=True)
def test_update_user_subscription_success(user_service, subscription_service, user_subscription_service):
    # Create initial data
    user_service.create_user(3, "nick3", "ACTIVATED_USER")
    subscription_service.create_subscription(3, Decimal("150.00"), 7, "P1M", "ACTIVATED_USER")
    subscription_service.create_subscription(4, Decimal("300.00"), 15, "P1Y", "ACTIVATED_USER")
    user_subscription_service.create_user_subscription(3, 3, "2024-12-31")

    # Update to new subscription
    user_subscription_service.update_user_subscription(3, 4, "2025-12-31")
    user_sub = user_subscription_service.get_user_subscription(3)

    assert user_sub.subscription.id == 4
    assert user_sub.subscription.price_in_rub == Decimal("300.00")
    assert user_sub.expiry_date == "2025-12-31"

@auto_transaction(always_rollback=True)
def test_update_user_subscription_not_exists(user_subscription_service):
    with pytest.raises(EntityNotExistsException):
        user_subscription_service.update_user_subscription(500000, 1, "2024-12-31")

@auto_transaction(always_rollback=True)
def test_delete_user_subscription_success(user_service, subscription_service, user_subscription_service):
    # Create data
    user_service.create_user(4, "nick4", "ACTIVATED_USER")
    subscription_service.create_subscription(5, Decimal("250.00"), 12, "P1M", "ACTIVATED_USER")
    user_subscription_service.create_user_subscription(4, 5, "2024-12-31")
    # Delete
    user_subscription_service.delete_user_subscription(4)
    assert user_subscription_service.get_user_subscription(4) is None

@auto_transaction(always_rollback=True)
def test_delete_user_subscription_not_exists(user_subscription_service):
    with pytest.raises(EntityNotExistsException):
        user_subscription_service.delete_user_subscription(123456)