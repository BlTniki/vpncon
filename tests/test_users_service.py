import pytest
from vpncon.users.service import UserServiceCRUD
from vpncon.users.model import Role
from vpncon.users.crud import delete_user
from vpncon.users.service import EntityAlreadyExistsException, EntityNotExistsException

# Для тестов предполагается, что тестовая БД уже настроена и переменные окружения корректны

@pytest.fixture
def user_service():
    return UserServiceCRUD()

@pytest.fixture
def test_user_id():
    return 123456789

@pytest.fixture(autouse=True)
def cleanup_user(test_user_id):
    # Удаляем пользователя до и после теста
    delete_user(test_user_id)
    yield
    delete_user(test_user_id)

def test_create_and_get_user(user_service, test_user_id):
    user_service.create_user(test_user_id, "testnick", Role.ACTIVATED_USER)
    user = user_service.get_user(test_user_id)
    assert user is not None
    assert user.telegram_id == test_user_id
    assert user.telegram_nick == "testnick"
    assert user.role == Role.ACTIVATED_USER

def test_create_user_already_exists(user_service, test_user_id):
    user_service.create_user(test_user_id, "testnick", Role.ADMIN)
    with pytest.raises(EntityAlreadyExistsException):
        user_service.create_user(test_user_id, "testnick2", Role.ADMIN)
# Добавить тест на удаление пользователя
def test_delete_user(user_service, test_user_id):
    user_service.create_user(test_user_id, "nick", Role.ACTIVATED_USER)
    user_service.get_user(test_user_id)  # exists
    delete_user(test_user_id)
    assert user_service.get_user(test_user_id) is None

def test_update_telegram_nick(user_service, test_user_id):
    user_service.create_user(test_user_id, "oldnick", Role.DEACTIVATED_USER)
    user_service.update_telegram_nick(test_user_id, "newnick")
    user = user_service.get_user(test_user_id)
    assert user.telegram_nick == "newnick"

def test_update_role(user_service, test_user_id):
    user_service.create_user(test_user_id, "nick", Role.ACTIVATED_CLOSE_USER)
    user_service.update_role(test_user_id, Role.ADMIN)
    user = user_service.get_user(test_user_id)
    assert user.role == Role.ADMIN

def test_get_user_not_exists(user_service):
    with pytest.raises(EntityNotExistsException):
        user_service.update_telegram_nick(999999999, "nick")
    with pytest.raises(EntityNotExistsException):
        user_service.update_role(999999999, Role.ACTIVATED_USER)
