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
def create_user(telegram_id: int, telegram_nick: str, role: str) -> None:
    """Создаёт нового пользователя.
    Если пользователь с таким telegram_id уже существует, бросает исключение.
    Args:
        telegram_id (int): Идентификатор пользователя в Telegram.
        telegram_nick (str): Никнейм пользователя в Telegram.
        role (str): Роль пользователя.
    """

    executor = get_db_executor()
    query = f"""
        INSERT INTO users ({User.get_model_fields_joined()})
        VALUES (%(telegram_id)s, %(telegram_nick)s, %(role)s)
    """
    params: dict[str, Any] = {
        'telegram_id': telegram_id,
        'telegram_nick': telegram_nick,
        'role': role
    }
    try:
        executor.execute(query, **params)
    except UniqueConstraintError as exc:
        # Абстрагированная проверка по имени класса
        raise UniqueConstraintError(
            f"User with telegram_id={telegram_id} already exists"
        ) from exc

# def update_user(telegram_id:int, **fields:Any):
#     with engine.connect() as conn:
#         stmt = update(users).where(users.c.telegram_id == telegram_id).values(**fields)
#         conn.execute(stmt)
#         conn.commit()

# def delete_user(telegram_id: int):
#     with engine.connect() as conn:
#         stmt = delete(users).where(users.c.telegram_id == telegram_id)
#         conn.execute(stmt)
#         conn.commit()