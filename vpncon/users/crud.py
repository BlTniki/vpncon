from typing import Any
from venv import logger
from vpncon.db import auto_transaction, get_db_executor, UniqueConstraintError
from .model import User


@auto_transaction
def get_user(telegram_id:int) -> User | None:
    """Получает пользователя по его telegram_id.
    Args:
        telegram_id (int): Идентификатор пользователя в Telegram.
    Returns:
        User | None: Экземпляр User, если пользователь найден, иначе None.
    """
    executor = get_db_executor()

    query = f"""
        SELECT
            {User.get_model_fields_joined()}
        FROM users WHERE telegram_id = %(telegram_id)s
    """
    params:dict[str, Any] = {
        'telegram_id': telegram_id
    }
    result = executor.execute(query, **params)
    if not result:
        return None
    if len(result) > 1:
        raise ValueError(f"Multiple users found with telegram_id={telegram_id}")
    logger.debug("User found: %s", result)
    return User.from_raw(result[0])

@auto_transaction
def create_user(user:User) -> None:
    """Создаёт нового пользователя.
    Если пользователь с таким telegram_id уже существует, бросает исключение.
    Args:
        user (User): Экземпляр пользователя для создания.
    """

    executor = get_db_executor()
    query = f"""
        INSERT INTO users ({User.get_model_fields_joined()})
        VALUES (%(telegram_id)s, %(telegram_nick)s, %(role)s)
    """
    params: dict[str, Any] = {
        'telegram_id': user.telegram_id,
        'telegram_nick': user.telegram_nick,
        'role': user.role
    }
    try:
        executor.execute(query, **params)
    except UniqueConstraintError as exc:
        # Абстрагированная проверка по имени класса
        raise UniqueConstraintError(
            f"User with telegram_id={user.telegram_id} already exists"
        ) from exc

@auto_transaction
def update_user(user:User) -> None:
    """Обновляет данные пользователя.

    Args:
        user (User): Экземпляр пользователя с обновлёнными данными.
    """
    executor = get_db_executor()
    query = f"""
        UPDATE users
        SET telegram_nick = %(telegram_nick)s,
            role = %(role)s
        WHERE telegram_id = %(telegram_id)s
    """
    params: dict[str, Any] = {
        'telegram_id': user.telegram_id,
        'telegram_nick': user.telegram_nick,
        'role': user.role
    }
    executor.execute(query, **params)

@auto_transaction
def delete_user(telegram_id: int) -> None:
    """Удаляет пользователя по его telegram_id.

    Args:
        telegram_id (int): Идентификатор пользователя в Telegram.
    """
    executor = get_db_executor()
    query = """
        DELETE FROM users WHERE telegram_id = %(telegram_id)s
    """
    params: dict[str, Any] = {
        'telegram_id': telegram_id
    }
    executor.execute(query, **params)