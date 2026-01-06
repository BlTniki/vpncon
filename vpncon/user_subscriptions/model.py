from typing import Any
from dataclasses import dataclass
from decimal import Decimal

from vpncon.db import DataModel
from vpncon.subscriptions.model import Subscription
from vpncon.users.model import Role, User


@dataclass(frozen=True)
class UserSubscription(DataModel):
    """Модель подписки пользователя."""
    user: User
    subscription: Subscription
    expiry_date: str  # DATE as string, e.g., '2024-12-31'

    @staticmethod
    def from_raw(raw: tuple[Any, ...]) -> 'UserSubscription':
        """Создаёт экземпляр `UserSubscription` из сырых данных, полученных из БД.

        Args:
            raw (tuple[Any, ...]): Сырые данные из БД.

        Returns:
            UserSubscription: Экземпляр `UserSubscription`.
        Raises:
            ValueError: Если поля не приводятся к нужным типам.
        """
        fields = [
            *list(map(lambda s: 'user_'+s, User.get_model_fields())),
            *list(map(lambda s: 'subscription_'+s, Subscription.get_model_fields())),
            'expiry_date'
        ]
        data = dict(zip(fields, raw))
        try:
            user_telegram_id = int(data['user_telegram_id'])
            user_telegram_nick = str(data['user_telegram_nick'])
            user_role = Role(data['user_role'])
            subscription_subscription_id = int(data['subscription_id'])
            subscription_price_in_rub = Decimal(data['subscription_price_in_rub'])
            subscription_allowed_peers = int(data['subscription_allowed_peers'])
            subscription_period = str(data['subscription_period'])
            subscription_role = Role(data['subscription_role'])
            expiry_date = str(data['expiry_date'])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Invalid data for UserSubscription: {data}"
            ) from exc

        return UserSubscription(
            user=User(
                telegram_id=user_telegram_id,
                telegram_nick=user_telegram_nick,
                role=user_role
            ),
            subscription=Subscription(
                id=subscription_subscription_id,
                price_in_rub=subscription_price_in_rub,
                allowed_peers=subscription_allowed_peers,
                period=subscription_period,
                role=subscription_role
            ),
            expiry_date=expiry_date
        )