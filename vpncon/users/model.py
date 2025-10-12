from typing import Any
from dataclasses import dataclass
from enum import StrEnum

from vpncon.db import DataModel


class Role(StrEnum):
    """Словарь ролей пользователя."""
    ADMIN = "ADMIN"
    DEACTIVATED_USER = "DEACTIVATED_USER"
    ACTIVATED_USER = "ACTIVATED_USER"
    ACTIVATED_CLOSE_USER = "ACTIVATED_CLOSE_USER"


@dataclass(frozen=True)
class User(DataModel):
    """Модель пользователя."""
    telegram_id: int
    telegram_nick: str
    role: Role

    @staticmethod
    def from_raw(raw: tuple[Any, ...]) -> 'User':
        """Создаёт экземпляр `User` из сырых данных, полученных из БД.

        Args:
            raw (tuple[Any, ...]): Сырые данные из БД.

        Returns:
            User: Экземпляр `User`.
        Raises:
            ValueError: Если поля не приводятся к нужным типам.
        """
        fields = User.get_model_fields()
        data = dict(zip(fields, raw))
        try:
            telegram_id = int(data['telegram_id'])
            telegram_nick = str(data['telegram_nick'])
            role = Role(data['role'])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Invalid data for User: {data}"
            ) from exc

        return User(
            telegram_id=telegram_id,
            telegram_nick=telegram_nick,
            role=role
        )
