from typing import Any
from dataclasses import dataclass

from vpncon.db import DataModel


@dataclass(frozen=True)
class Host(DataModel):
    """Модель хоста."""
    id: int
    name: str
    ip_address: str
    port: int
    host_password: str

    @staticmethod
    def from_raw(raw: tuple[Any, ...]) -> 'Host':
        """Создаёт экземпляр `Subscription` из сырых данных, полученных из БД.

        Args:
            raw (tuple[Any, ...]): Сырые данные из БД.

        Returns:
            Subscription: Экземпляр `Subscription`.
        Raises:
            ValueError: Если поля не приводятся к нужным типам.
        """
        fields = Host.get_model_fields()
        data = dict(zip(fields, raw))
        try:
            host_id = int(data['id'])
            name = str(data['name'])
            ip_address = str(data['ip_address'])
            port = int(data['port'])
            host_password = str(data['host_password'])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Invalid data for Host: {data}"
            ) from exc

        return Host(
            id=host_id,
            name=name,
            ip_address=ip_address,
            port=port,
            host_password=host_password
        )
