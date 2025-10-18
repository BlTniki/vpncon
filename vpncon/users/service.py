
from abc import ABC, abstractmethod

from vpncon.db.db import UniqueConstraintError

from .crud import create_user, get_user, update_user, delete_user
from vpncon.exceptions import EntityAlreadyExistsException, EntityNotExistsException
from .model import User, Role





class UserService(ABC):

    @abstractmethod
    def create_user(self, telegram_id: int, telegram_nick: str, role: str) -> None:
        pass

    @abstractmethod
    def get_user(self, telegram_id: int) -> User | None:
        pass

    @abstractmethod
    def update_user(self, telegram_id: int, telegram_nick: str, role: str) -> None:
        pass

    @abstractmethod
    def delete_user(self, telegram_id: int) -> None:
        pass


class UserServiceCRUD(UserService):
    def create_user(self, telegram_id: int, telegram_nick: str, role: str):
        role = Role(role)
        user = User(telegram_id, telegram_nick, role)
        try:
            create_user(user)
        except UniqueConstraintError as exc:
            raise EntityAlreadyExistsException(
                f"User with telegram_id={telegram_id} already exists"
            ) from exc

    def get_user(self, telegram_id: int) -> User | None:
        return get_user(telegram_id)

    def update_user(self, telegram_id: int, telegram_nick: str, role: str) -> None:
        if get_user(telegram_id) is None:
            raise EntityNotExistsException(f"User with telegram_id={telegram_id} not found")
        role = Role(role)
        user = User(telegram_id, telegram_nick, role)
        return update_user(user)

    def delete_user(self, telegram_id: int):
        if get_user(telegram_id) is None:
            raise EntityNotExistsException(f"User with telegram_id={telegram_id} not found")
        return delete_user(telegram_id)
