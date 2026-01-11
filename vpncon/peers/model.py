from typing import Any
from dataclasses import dataclass

from vpncon.db import DataModel
from vpncon.hosts.model import Host
from vpncon.users.model import User, Role


@dataclass(frozen=True)
class Peer(DataModel):
    """Модель пира."""
    user: User
    host: Host
    conf_name: str
    peer_ip: str
    is_active: bool

    @staticmethod
    def from_raw(raw: tuple[Any, ...]) -> 'Peer':
        """Создаёт экземпляр `Peer` из сырых данных, полученных из БД.

        Args:
            raw (tuple[Any, ...]): Сырые данные из БД.

        Returns:
            Peer: Экземпляр `Peer`.
        Raises:
            ValueError: Если поля не приводятся к нужным типам.
        """
        fields = [
            *list(map(lambda s: 'user_'+s, User.get_model_fields())),
            *list(map(lambda s: 'host_'+s, Host.get_model_fields())),
            'conf_name',
            'peer_ip',
            'is_active'
        ]
        data = dict(zip(fields, raw))
        try:
            user_telegram_id = int(data['user_telegram_id'])
            user_telegram_nick = str(data['user_telegram_nick'])
            user_role = Role(data['user_role'])
            host_id = int(data['host_id'])
            host_name = str(data['host_name'])
            host_ip_address = str(data['host_ip_address'])
            host_port = int(data['host_port'])
            host_host_password = str(data['host_host_password'])
            conf_name = str(data['conf_name'])
            peer_ip = str(data['peer_ip'])
            is_active = bool(data['is_active'])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Invalid data for Peer: {data}"
            ) from exc

        return Peer(
            user=User(
                telegram_id=user_telegram_id,
                telegram_nick=user_telegram_nick,
                role=user_role
            ),
            host=Host(
                id=host_id,
                name=host_name,
                ip_address=host_ip_address,
                port=host_port,
                host_password=host_host_password
            ),
            conf_name=conf_name,
            peer_ip=peer_ip,
            is_active=is_active
        )