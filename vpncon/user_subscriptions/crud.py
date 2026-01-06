import logging
from typing import Any
from vpncon.db import auto_transaction, get_db_executor, UniqueConstraintError
from .model import UserSubscription

logger = logging.getLogger(__name__)


@auto_transaction()
def get_user_subscription(telegram_id:int) -> UserSubscription | None:
    """Получает подписку пользователя по его telegram_id.
    Args:
        telegram_id (int): Идентификатор пользователя в Telegram.
    Returns:
        UserSubscription | None: Экземпляр UserSubscription, если подписка найдена, иначе None.
    """
    executor = get_db_executor()

    query = """
        SELECT
            u.*,
            s.*,
            us.expiry_date
        FROM user_subscriptions us
        JOIN users u ON u.telegram_id = us.user_id
        JOIN subscriptions s ON s.id = us.subscription_id
        WHERE us.user_id = %(telegram_id)s
    """
    params:dict[str, Any] = {
        'telegram_id': telegram_id
    }
    result = executor.execute(query, **params)
    if not result:
        return None
    if len(result) > 1:
        raise ValueError(f"Multiple user subscriptions found with telegram_id={telegram_id}")
    logger.debug("UserSubscription found: %s", result)
    return UserSubscription.from_raw(result[0])

@auto_transaction()
def create_user_subscription(user_id: int, subscription_id: int, expiry_date: str) -> None:
    """Создаёт новую подписку пользователю.
    Если у пользователя с таким telegram_id уже существует подписка, то бросает исключение.
    Args:
        user_id (int): Идентификатор пользователя в Telegram.
        subscription_id (int): Идентификатор подписки.
        expiry_date (str): Дата окончания подписки.
    """

    executor = get_db_executor()
    query = """
        INSERT INTO user_subscriptions (user_id, subscription_id, expiry_date)
        VALUES (%(user_id)s, %(subscription_id)s, %(expiry_date)s)
    """
    params: dict[str, Any] = {
        'user_id': user_id,
        'subscription_id': subscription_id,
        'expiry_date': expiry_date
    }
    try:
        executor.execute(query, **params)
        logger.info(
            "UserSubscription created: %s, %s, %s",
            user_id,
            subscription_id,
            expiry_date
        )
    except UniqueConstraintError as exc:
        # Абстрагированная проверка по имени класса
        raise UniqueConstraintError(
            f"UserSubscription for User with telegram_id={user_id}"
            +  "already exists"
        ) from exc

@auto_transaction()
def update_user_subscription(user_id: int, subscription_id: int, expiry_date: str) -> None:
    """Обновляет данные подписки пользователя.

    Args:
        user_id (int): Идентификатор пользователя в Telegram.
        subscription_id (int): Идентификатор подписки.
        expiry_date (str): Дата окончания подписки.
    """
    executor = get_db_executor()
    query = """
        UPDATE user_subscriptions
        SET subscription_id = %(subscription_id)s,
            expiry_date = %(expiry_date)s
        WHERE user_id = %(user_id)s
    """
    params: dict[str, Any] = {
        'user_id': user_id,
        'subscription_id': subscription_id,
        'expiry_date': expiry_date
    }
    executor.execute(query, **params)
    logger.info(
        "UserSubscription updated updated: %s, %s, %s",
        user_id,
        subscription_id,
        expiry_date
    )

@auto_transaction()
def delete_user(telegram_id: int) -> None:
    """Удаляет подписку пользователя по его telegram_id.

    Args:
        telegram_id (int): Идентификатор пользователя в Telegram.
    """
    executor = get_db_executor()
    query = """
        DELETE FROM user_subscriptions WHERE user_id = %(telegram_id)s
    """
    params: dict[str, Any] = {
        'telegram_id': telegram_id
    }
    executor.execute(query, **params)
    logger.info("UserSubscription deleted: %s", telegram_id)