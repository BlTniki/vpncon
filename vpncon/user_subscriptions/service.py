import logging
from abc import ABC, abstractmethod

from vpncon.db import auto_transaction
from vpncon.db.db import UniqueConstraintError

from vpncon.exceptions import EntityAlreadyExistsException, EntityNotExistsException
from .crud import (
    create_user_subscription,
    get_user_subscription,
    update_user_subscription,
    delete_user
)
from .model import UserSubscription

logger = logging.getLogger(__name__)




class UserSubscriptionService(ABC):

    @abstractmethod
    def create_user_subscription(
        self, telegram_id: int, subscription_id: int, expiry_date: str
    ) -> None:
        pass

    @abstractmethod
    def get_user_subscription(self, telegram_id: int) -> UserSubscription | None:
        pass

    @abstractmethod
    def update_user_subscription(
        self, telegram_id: int, subscription_id: int, expiry_date: str
    ) -> None:
        pass

    @abstractmethod
    def delete_user_subscription(self, telegram_id: int) -> None:
        pass


class UserSubscriptionServiceCRUD(UserSubscriptionService):
    @auto_transaction()
    def create_user_subscription(
        self, telegram_id: int, subscription_id: int, expiry_date: str
    ) -> None:
        logger.info("Creating user subscription for telegram_id: %s", telegram_id)
        try:
            create_user_subscription(telegram_id, subscription_id, expiry_date)
            logger.info("User subscription created successfully: %s", telegram_id)
        except UniqueConstraintError as exc:
            logger.warning("Failed to create user subscription, already exists: %s", telegram_id)
            raise EntityAlreadyExistsException(
                f"User subscription for telegram_id={telegram_id} already exists"
            ) from exc

    @auto_transaction()
    def get_user_subscription(self, telegram_id: int) -> UserSubscription | None:
        logger.debug("Retrieving user subscription with telegram_id: %s", telegram_id)
        return get_user_subscription(telegram_id)

    @auto_transaction()
    def update_user_subscription(
        self, telegram_id: int, subscription_id: int, expiry_date: str
    ) -> None:
        logger.info("Updating user subscription with telegram_id: %s", telegram_id)
        if get_user_subscription(telegram_id) is None:
            logger.warning("User subscription not found for update: %s", telegram_id)
            raise EntityNotExistsException(
                f"User subscription with telegram_id={telegram_id} not found"
            )
        update_user_subscription(telegram_id, subscription_id, expiry_date)
        logger.info("User subscription updated successfully: %s", telegram_id)

    @auto_transaction()
    def delete_user_subscription(self, telegram_id: int) -> None:
        logger.info("Deleting user subscription with telegram_id: %s", telegram_id)
        if get_user_subscription(telegram_id) is None:
            logger.warning("User subscription not found for deletion: %s", telegram_id)
            raise EntityNotExistsException(
                f"User subscription with telegram_id={telegram_id} not found"
            )
        delete_user(telegram_id)
        logger.info("User subscription deleted successfully: %s", telegram_id)
