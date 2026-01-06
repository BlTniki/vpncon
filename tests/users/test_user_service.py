import pytest
from vpncon.db import auto_transaction
from vpncon.users.service import UserServiceCRUD
from vpncon.users.model import User, Role
from vpncon.exceptions import EntityAlreadyExistsException, EntityNotExistsException

@pytest.fixture
def service():
    return UserServiceCRUD()

@auto_transaction(always_rollback=True)
def test_create_user_success(service):
    service.create_user(telegram_id=1, telegram_nick="nick1", role="ACTIVATED_USER")
    user = service.get_user(1)
    assert user is not None
    assert user.telegram_id == 1
    assert user.telegram_nick == "nick1"
    assert user.role == Role.ACTIVATED_USER

@auto_transaction(always_rollback=True)
def test_create_user_conflict(service):
    service.create_user(2, "nick2", "ADMIN")
    with pytest.raises(EntityAlreadyExistsException):
        service.create_user(2, "nick2_dup", "ADMIN")

@auto_transaction(always_rollback=True)
def test_get_user_not_exists(service):
    assert service.get_user(999999) is None

@auto_transaction(always_rollback=True)
def test_update_user_success(service):
    service.create_user(3, "nick3", "ACTIVATED_USER")

    service.update_user(3, "nick3_updated", "ADMIN")
    user = service.get_user(3)

    assert user.telegram_nick == "nick3_updated"
    assert user.role == Role.ADMIN

@auto_transaction(always_rollback=True)
def test_update_user_not_exists(service):
    with pytest.raises(EntityNotExistsException):
        service.update_user(500000, "nickX", "ACTIVATED_USER")

@auto_transaction(always_rollback=True)
def test_delete_user_success(service):
    service.create_user(4, "nick4", "ACTIVATED_USER")
    service.delete_user(4)
    assert service.get_user(4) is None

@auto_transaction(always_rollback=True)
def test_delete_user_not_exists(service):
    with pytest.raises(EntityNotExistsException):
        service.delete_user(123456)
