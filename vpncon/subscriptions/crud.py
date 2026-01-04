import logging
from typing import Any
from vpncon.db import auto_transaction, get_db_executor, UniqueConstraintError
from vpncon.users.model import Role
from .model import Subscription

logger = logging.getLogger(__name__)


@auto_transaction
def get_subscription(subscription_id: int) -> Subscription | None:
    """Получает подписку по её id.
    Args:
        subscription_id (int): Идентификатор подписки.
    Returns:
        Subscription | None: Экземпляр Subscription, если подписка найдена, иначе None.
    """
    executor = get_db_executor()

    query = f"""
        SELECT
            {Subscription.get_model_fields_joined()}
        FROM subscriptions WHERE id = %(subscription_id)s
    """
    params: dict[str, Any] = {
        'subscription_id': subscription_id
    }
    result = executor.execute(query, **params)
    if not result:
        return None
    if len(result) > 1:
        raise ValueError(f"Multiple subscriptions found with id={subscription_id}")
    logger.debug("Subscription found: %s", result)
    return Subscription.from_raw(result[0])


@auto_transaction
def get_subscriptions_by_role(role: Role) -> list[Subscription]:
    """Получает подписки с определённой ролью.
    Args:
        role (Role): Роль подписки.
    Returns:
        list[Subscription]: Список подписок с указанной ролью.
    """
    executor = get_db_executor()

    query = f"""
        SELECT
            {Subscription.get_model_fields_joined()}
        FROM subscriptions WHERE role = %(role)s
    """
    params: dict[str, Any] = {
        'role': role
    }
    result = executor.execute(query, **params)
    subscriptions: list[Subscription] = []
    for row in result:
        subscriptions.append(Subscription.from_raw(row))
    logger.debug("Found %d subscriptions with role %s", len(subscriptions), role)
    return subscriptions


@auto_transaction
def create_subscription(subscription: Subscription) -> None:
    """Создаёт новую подписку.
    Если подписка с таким id уже существует, бросает исключение.
    Args:
        subscription (Subscription): Экземпляр подписки для создания.
    """
    executor = get_db_executor()
    query = f"""
        INSERT INTO subscriptions ({Subscription.get_model_fields_joined()})
        VALUES (%(id)s, %(price_in_rub)s, %(allowed_peers)s, %(period)s, %(role)s)
    """
    params: dict[str, Any] = {
        'id': subscription.id,
        'price_in_rub': subscription.price_in_rub,
        'allowed_peers': subscription.allowed_peers,
        'period': subscription.period,
        'role': subscription.role
    }
    try:
        executor.execute(query, **params)
        logger.info("Subscription created: %s", subscription.id)
    except UniqueConstraintError as exc:
        raise UniqueConstraintError(
            f"Subscription with id={subscription.id} already exists"
        ) from exc


@auto_transaction
def update_subscription(subscription: Subscription) -> None:
    """Обновляет данные подписки.
    Args:
        subscription (Subscription): Экземпляр подписки с обновлёнными данными.
    """
    executor = get_db_executor()
    query = """
        UPDATE subscriptions
        SET price_in_rub = %(price_in_rub)s,
            allowed_peers = %(allowed_peers)s,
            period = %(period)s,
            role = %(role)s
        WHERE id = %(id)s
    """
    params: dict[str, Any] = {
        'id': subscription.id,
        'price_in_rub': subscription.price_in_rub,
        'allowed_peers': subscription.allowed_peers,
        'period': subscription.period,
        'role': subscription.role
    }
    executor.execute(query, **params)
    logger.info("Subscription updated: %s", subscription.id)


@auto_transaction
def delete_subscription(subscription_id: int) -> None:
    """Удаляет подписку по её id.
    Args:
        subscription_id (int): Идентификатор подписки.
    """
    executor = get_db_executor()
    query = """
        DELETE FROM subscriptions WHERE id = %(subscription_id)s
    """
    params: dict[str, Any] = {
        'subscription_id': subscription_id
    }
    executor.execute(query, **params)
    logger.info("Subscription deleted: %s", subscription_id)