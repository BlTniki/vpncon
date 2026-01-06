from abc import ABC, abstractmethod
import logging
from decimal import Decimal

from vpncon.db import auto_transaction
from vpncon.db.db import UniqueConstraintError

from vpncon.exceptions import EntityAlreadyExistsException, EntityNotExistsException
from .crud import create_subscription, get_subscription, update_subscription, delete_subscription, get_subscriptions_by_role
from .model import Subscription, Role

logger = logging.getLogger(__name__)


class SubscriptionService(ABC):

    @abstractmethod
    def create_subscription(self, subscription_id: int, price_in_rub: Decimal, allowed_peers: int, period: str, role: str) -> None:
        pass

    @abstractmethod
    def get_subscription(self, subscription_id: int) -> Subscription | None:
        pass

    @abstractmethod
    def get_subscriptions_by_role(self, role: str) -> list[Subscription]:
        pass

    @abstractmethod
    def update_subscription(self, subscription_id: int, price_in_rub: Decimal, allowed_peers: int, period: str, role: str) -> None:
        pass

    @abstractmethod
    def delete_subscription(self, subscription_id: int) -> None:
        pass


class SubscriptionServiceCRUD(SubscriptionService):
    @auto_transaction()
    def create_subscription(self, subscription_id: int, price_in_rub: Decimal, allowed_peers: int, period: str, role: str):
        logger.info("Creating subscription with id: %s", subscription_id)
        role = Role(role)
        subscription = Subscription(subscription_id, price_in_rub, allowed_peers, period, role)
        try:
            create_subscription(subscription)
            logger.info("Subscription created successfully: %s", subscription_id)
        except UniqueConstraintError as exc:
            logger.warning("Failed to create subscription, already exists: %s", subscription_id)
            raise EntityAlreadyExistsException(
                f"Subscription with id={subscription_id} already exists"
            ) from exc

    @auto_transaction()
    def get_subscription(self, subscription_id: int) -> Subscription | None:
        logger.debug("Retrieving subscription with id: %s", subscription_id)
        return get_subscription(subscription_id)

    @auto_transaction()
    def get_subscriptions_by_role(self, role: str) -> list[Subscription]:
        logger.debug("Retrieving subscriptions with role: %s", role)
        role = Role(role)
        return get_subscriptions_by_role(role)

    @auto_transaction()
    def update_subscription(self, subscription_id: int, price_in_rub: Decimal, allowed_peers: int, period: str, role: str) -> None:
        logger.info("Updating subscription with id: %s", subscription_id)
        if get_subscription(subscription_id) is None:
            logger.warning("Subscription not found for update: %s", subscription_id)
            raise EntityNotExistsException(f"Subscription with id={subscription_id} not found")
        role_enum = Role(role)
        subscription = Subscription(subscription_id, price_in_rub, allowed_peers, period, role_enum)
        update_subscription(subscription)
        logger.info("Subscription updated successfully: %s", subscription_id)

    @auto_transaction()
    def delete_subscription(self, subscription_id: int):
        logger.info("Deleting subscription with id: %s", subscription_id)
        if get_subscription(subscription_id) is None:
            logger.warning("Subscription not found for deletion: %s", subscription_id)
            raise EntityNotExistsException(f"Subscription with id={subscription_id} not found")
        delete_subscription(subscription_id)
        logger.info("Subscription deleted successfully: %s", subscription_id)