
import logging
from abc import ABC, abstractmethod

from vpncon.db import auto_transaction
from vpncon.db.db import UniqueConstraintError

from .crud import create_user, get_user, update_user, delete_user
from vpncon.exceptions import EntityAlreadyExistsException, EntityNotExistsException
from .model import User, Role

logger = logging.getLogger(__name__)





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
    @auto_transaction()
    def create_user(self, telegram_id: int, telegram_nick: str, role: str):
        logger.info("Creating user with telegram_id: %s", telegram_id)
        role = Role(role)
        user = User(telegram_id, telegram_nick, role)
        try:
            create_user(user)
            logger.info("User created successfully: %s", telegram_id)
        except UniqueConstraintError as exc:
            logger.warning("Failed to create user, already exists: %s", telegram_id)
            raise EntityAlreadyExistsException(
                f"User with telegram_id={telegram_id} already exists"
            ) from exc

    @auto_transaction()
    def get_user(self, telegram_id: int) -> User | None:
        logger.debug("Retrieving user with telegram_id: %s", telegram_id)
        return get_user(telegram_id)

    @auto_transaction()
    def update_user(self, telegram_id: int, telegram_nick: str, role: str) -> None:
        logger.info("Updating user with telegram_id: %s", telegram_id)
        if get_user(telegram_id) is None:
            logger.warning("User not found for update: %s", telegram_id)
            raise EntityNotExistsException(f"User with telegram_id={telegram_id} not found")
        role = Role(role)
        user = User(telegram_id, telegram_nick, role)
        update_user(user)
        logger.info("User updated successfully: %s", telegram_id)

    @auto_transaction()
    def delete_user(self, telegram_id: int):
        logger.info("Deleting user with telegram_id: %s", telegram_id)
        if get_user(telegram_id) is None:
            logger.warning("User not found for deletion: %s", telegram_id)
            raise EntityNotExistsException(f"User with telegram_id={telegram_id} not found")
        delete_user(telegram_id)
        logger.info("User deleted successfully: %s", telegram_id)
