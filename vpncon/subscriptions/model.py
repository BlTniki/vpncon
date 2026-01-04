from typing import Any
from dataclasses import dataclass
from decimal import Decimal

from vpncon.db import DataModel
from vpncon.users.model import Role


@dataclass(frozen=True)
class Subscription(DataModel):
    """Модель подписки."""
    id: int
    price_in_rub: Decimal
    allowed_peers: int
    period: str  # INTERVAL as string, e.g., '1 month', '30 days'
    role: Role

    @staticmethod
    def from_raw(raw: tuple[Any, ...]) -> 'Subscription':
        """Создаёт экземпляр `Subscription` из сырых данных, полученных из БД.

        Args:
            raw (tuple[Any, ...]): Сырые данные из БД.

        Returns:
            Subscription: Экземпляр `Subscription`.
        Raises:
            ValueError: Если поля не приводятся к нужным типам.
        """
        fields = Subscription.get_model_fields()
        data = dict(zip(fields, raw))
        try:
            subscription_id = int(data['id'])
            price_in_rub = Decimal(data['price_in_rub'])
            allowed_peers = int(data['allowed_peers'])
            period = str(data['period'])
            role = Role(data['role'])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Invalid data for Subscription: {data}"
            ) from exc

        return Subscription(
            id=subscription_id,
            price_in_rub=price_in_rub,
            allowed_peers=allowed_peers,
            period=period,
            role=role
        )