from typing import Any
from .model import User
from vpncon.db import auto_transaction, get_db_executor, UniqueConstraintError


@auto_transaction
def get_user(telegram_id:int) -> User | None:
    """Получает пользователя по его telegram_id.
    Args:
        telegram_id (int): Идентификатор пользователя в Telegram.
    Returns:
        User | None: Экземпляр User, если пользователь найден, иначе None.
    """
    executor = get_db_executor()
    query = "SELECT %(model_cols)s FROM users WHERE telegram_id = %(telegram_id)s"
    params:dict[str, Any] = {
        'model_cols': ', '.join(User.get_model_fields()),
        'telegram_id': telegram_id
    }
    result = executor.execute(query, **params)
    if not result:
        return None
    if len(result) > 1:
        raise ValueError(f"Multiple users found with telegram_id={telegram_id}")
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
    query = """
        INSERT INTO users (%(model_cols)s)
        VALUES (%(telegram_id)s, %(telegram_nick)s, %(role)s)
    """
    params: dict[str, Any] = {
        'model_cols': ', '.join(User.get_model_fields()),
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