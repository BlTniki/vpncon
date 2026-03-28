import logging
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import isodate

from vpncon.db import auto_transaction
from vpncon.exceptions import EntityValidationFailedException
from vpncon.peers import peer_service
from vpncon.subscriptions import subscription_service
from vpncon.subscriptions.model import Subscription
from vpncon.user_subscriptions import user_subscription_service, UserSubscription

logger = logging.getLogger(__name__)


class UserPeerSubscriptionManager:
    """Оркестратор взаимодействия user_subscriptions + peers."""

    def _ensure_user_can_activate_peers(self, telegram_id: int) -> bool:
        user_sub = user_subscription_service.get_user_subscription(telegram_id)
        if user_sub is None:
            logger.warning(
                "Negative verification result for user %s: no subscription found",
                telegram_id
            )
            return False

        user_peers = peer_service.get_all_peers_by_user(telegram_id)
        user_active_peers = [p for p in user_peers if p.is_active]
        if len(user_active_peers) >= user_sub.subscription.allowed_peers:
            logger.warning(
                "Negative verification result for user %s: maximum peers limit reached",
                telegram_id
            )
            return False

        return True

    def _handle_subscription_expired(self, telegram_id: int) -> None:
        logger.info("Subscription expired for user %s, deactivating all peers", telegram_id)
        peer_service.deactivate_all_peers(telegram_id)

    @auto_transaction()
    def create_peer(self, telegram_id: int, host_id: int, conf_name: str) -> None:
        if not self._ensure_user_can_activate_peers(telegram_id):
            logger.error(
                "Failed to create peer for user %s: user cannot activate more peers",
                telegram_id
            )
            raise EntityValidationFailedException(
                f"User with telegram_id={telegram_id} cannot activate more peers"
            )
        return peer_service.create_peer(telegram_id, host_id, conf_name)

    @auto_transaction()
    def activate_peer(self, telegram_id: int, conf_name: str) -> None:
        if not self._ensure_user_can_activate_peers(telegram_id):
            logger.error(
                "Failed to activate peer for user %s: user cannot activate more peers",
                telegram_id
            )
            raise EntityValidationFailedException(
                f"User with telegram_id={telegram_id} cannot activate more peers"
            )
        return peer_service.switch_peer_active_status(
            telegram_id, conf_name, True
        )

    @auto_transaction()
    def deactivate_peer(self, telegram_id: int, conf_name: str) -> None:
        return peer_service.switch_peer_active_status(
            telegram_id, conf_name, False
        )

    def _calc_new_expiry_date(self, cur_expiry_date:date, new_sub_duration:str) -> date:
        duration_parsed = isodate.parse_duration(new_sub_duration) # type: ignore
        if isinstance(duration_parsed, isodate.Duration):
            # Конвертируем Duration в relativedelta
            duration_parsed = relativedelta(
                years=duration_parsed.years,
                months=duration_parsed.months,
                days=duration_parsed.days,
            )
        return cur_expiry_date + duration_parsed

    def _create_user_subscription(
        self, telegram_id: int, new_sub: Subscription
    ) -> None:
        cur_expiry_date = date.today()
        new_expiry_date = self._calc_new_expiry_date(cur_expiry_date, new_sub.period)

        user_subscription_service.create_user_subscription(
            telegram_id, new_sub.id, new_expiry_date.isoformat()
        )
        logger.info(
            "Subscription %s created for user %s successfully",
            new_sub.id,
            telegram_id
        )

    def _extend_user_subscription(
        self, telegram_id: int, cur_user_sub: UserSubscription, new_sub: Subscription
    ) -> None:
        cur_expiry_date = date.fromisoformat(cur_user_sub.expiry_date)
        new_expiry_date = self._calc_new_expiry_date(cur_expiry_date, new_sub.period)

        user_subscription_service.update_user_subscription(
            telegram_id, new_sub.id, new_expiry_date.isoformat()
        )

        # Если id старой и новой подписки не совпадают, то это означает, что пользователь перешёл на 
        # другой тарифный план, и мы должны деактивировать все его пиры
        if cur_user_sub.subscription.id != new_sub.id:
            logger.info(
                "User %s switched subscription from %s to %s, deactivating all peers",
                telegram_id,
                cur_user_sub.subscription.id,
                new_sub.id
            )
            self._handle_subscription_expired(telegram_id)

        logger.info(
            "Subscription %s updated for user %s successfully",
            new_sub.id,
            telegram_id
        )

    @auto_transaction()
    def add_subscription_to_user(self, telegram_id: int, subscription_id: int) -> UserSubscription:
        """Добавляет подписку к пользователю. Если подписка уже есть, то продлевает её.
            Если пользователь перешёл на другой тарифный план, то деактивирует все его пиры.

            Начисляет подписку максимально тупо, без сложной логики пересчёта отставшего времени.
            Просто, если подписка есть, то добавляет к её expiry_date период новой подписки.
            Если подписки нет, то создаёт новую с expiry_date = today + период новой подписки.
        """
        # Получаем текущую подписку пользователя
        cur_user_sub = user_subscription_service.get_user_subscription(telegram_id)

        # Получаем данные новой подписки
        new_sub = subscription_service.get_subscription(subscription_id)
        if new_sub is None:
            logger.error(
                "Failed to add subscription %s to user %s: subscription does not exist",
                subscription_id,
                telegram_id
            )
            raise EntityValidationFailedException(
                f"Subscription with id={subscription_id} does not exist"
            )

        if cur_user_sub:
            self._extend_user_subscription(telegram_id, cur_user_sub, new_sub)
        else:
            self._create_user_subscription(telegram_id, new_sub)

        new_user_sub = user_subscription_service.get_user_subscription(telegram_id)
        if new_user_sub is None:
            logger.error(
                "Failed to retrieve user subscription for user %s after adding subscription %s",
                telegram_id,
                subscription_id
            )
            raise RuntimeError(
                f"User subscription for telegram_id={telegram_id} was not found after adding subscription"
            )
        return new_user_sub
