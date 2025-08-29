
from abc import ABC, abstractmethod

from .crud import create_user, get_user, update_user
from ..exceptions import EntityAlreadyExistsException, EntityNotExistsException
from .model import User, Role





class UserService(ABC):

    @abstractmethod
    def create_user(self, telegram_id: int, telegram_nick: str, role: Role) -> None:
        pass

    @abstractmethod
    def get_user(self, telegram_id: int) -> User | None:
        pass

    @abstractmethod
    def update_telegram_nick(self, telegram_id: int, telegram_nick: str) -> None:
        pass

    @abstractmethod
    def update_role(self, telegram_id: int, role: Role) -> None:
        pass


class UserServiceCRUD(UserService):
    def create_user(self, telegram_id: int, telegram_nick: str, role: Role):
        if get_user(telegram_id) is not None:
            raise EntityAlreadyExistsException(
                f"User with telegram_id={telegram_id} already exists"
            )
        return create_user(telegram_id, telegram_nick, role)

    def get_user(self, telegram_id: int) -> User | None:
        row = get_user(telegram_id)
        if row is None:
            return None
        return User.from_row(row)

    def update_telegram_nick(self, telegram_id: int, telegram_nick: str):
        if get_user(telegram_id) is None:
            raise EntityNotExistsException(f"User with telegram_id={telegram_id} not found")
        return update_user(telegram_id, telegram_nick=telegram_nick)

    def update_role(self, telegram_id: int, role: Role):
        if get_user(telegram_id) is None:
            raise EntityNotExistsException(f"User with telegram_id={telegram_id} not found")
        return update_user(telegram_id, role=role)
