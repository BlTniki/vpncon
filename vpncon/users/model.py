from typing import Any
from sqlalchemy import Table, Column, BigInteger, String, Row
from ..db import metadata
from dataclasses import dataclass
from enum import StrEnum


users = Table(
    "users",
    metadata,
    Column("telegram_id", BigInteger, primary_key=True),
    Column("telegram_nick", String),
    Column("role", String),
)


class Role(StrEnum):
    """Словарь ролей пользователя."""
    ADMIN = "ADMIN"
    DEACTIVATED_USER = "DEACTIVATED_USER"
    ACTIVATED_USER = "ACTIVATED_USER"
    ACTIVATED_CLOSE_USER = "ACTIVATED_CLOSE_USER"


@dataclass(frozen=True)
class User:
    telegram_id: int
    telegram_nick: str
    role: Role

    @staticmethod
    def from_row(row:Row[Any]) -> 'User':
        return User(row.telegram_id, row.telegram_nick, Role(row.role))
