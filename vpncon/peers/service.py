import logging
from abc import ABC, abstractmethod

from vpncon.db import auto_transaction
from vpncon.db.db import UniqueConstraintError

from vpncon.exceptions import (
    EntityAlreadyExistsException,
    EntityNotExistsException,
    EntityValidationFailedException,
)
from .crud import (
    get_peer,
    get_all_peers_by_user,
    create_peer,
    delete_peer,
    switch_peer_active_status,
    pick_and_lock_peer_ip,
    release_peer_ip,
)
from .model import Peer
from .host_client import HostClient

logger = logging.getLogger(__name__)


class PeerService(ABC):

    @abstractmethod
    def create_peer(self, telegram_id: int, host_id: int, conf_name: str) -> None:
        pass

    @abstractmethod
    def get_peer(self, telegram_id: int, conf_name: str) -> Peer | None:
        pass

    @abstractmethod
    def get_all_peers_by_user(self, telegram_id: int) -> list[Peer]:
        pass

    @abstractmethod
    def switch_peer_active_status(
        self, telegram_id: int, conf_name: str, is_active: bool
    ) -> None:
        pass

    @abstractmethod
    def delete_peer(self, telegram_id: int, conf_name: str) -> None:
        pass

    @abstractmethod
    def deactivate_all_peers(self, telegram_id: int) -> None:
        pass

    @abstractmethod
    def get_peer_download_token(self, telegram_id: int, conf_name: str) -> str:
        pass


class PeerServiceCRUD(PeerService):
    @auto_transaction()
    def create_peer(self, telegram_id: int, host_id: int, conf_name: str) -> None:
        logger.info(
            "Creating peer with conf_name `%s` for telegram_id: %s",
            conf_name,
            telegram_id,
        )

        peer_ip = pick_and_lock_peer_ip(host_id)
        if peer_ip is None:
            logger.warning("No available IP address for host_id: %s", host_id)
            raise EntityValidationFailedException(
                f"No available IP address for host_id={host_id}"
            )

        try:
            create_peer(telegram_id, host_id, conf_name, peer_ip)
            logger.info("Peer created successfully: %s", telegram_id)
        except UniqueConstraintError as exc:
            logger.warning("Failed to create peer, already exists: %s", telegram_id)
            raise EntityAlreadyExistsException(
                f"Peer with conf_name={conf_name} for User with telegram_id={telegram_id} already exists"
            ) from exc

        created_peer = get_peer(telegram_id, conf_name)
        if created_peer is None:
            logger.error(
                "Peer creation failed unexpectedly for telegram_id: %s", telegram_id
            )
            raise RuntimeError(
                f"Peer with conf_name={conf_name} for User with telegram_id={telegram_id} was not created"
            )
        hc = HostClient(created_peer)
        try:
            hc.create_peer_on_host()
            logger.info(
                "peer with conf_name `%s` for telegram_id: %s created on host `%s successfully",
                conf_name,
                telegram_id,
                host_id,
            )
        except Exception as exc:
            raise RuntimeError("Failed to create peer on host") from exc

    @auto_transaction()
    def get_peer(self, telegram_id: int, conf_name: str) -> Peer | None:
        logger.debug(
            "Retrieving peer with telegram_id: %s and conf_name: %s",
            telegram_id,
            conf_name,
        )
        return get_peer(telegram_id, conf_name)

    @auto_transaction()
    def get_all_peers_by_user(self, telegram_id: int) -> list[Peer]:
        logger.debug("Retrieving all peers for telegram_id: %s", telegram_id)
        return get_all_peers_by_user(telegram_id)

    @auto_transaction()
    def switch_peer_active_status(
        self, telegram_id: int, conf_name: str, is_active: bool
    ) -> None:
        logger.info(
            "Switching peer active status for telegram_id: %s and conf_name: %s to %s",
            telegram_id,
            conf_name,
            is_active,
        )
        peer = get_peer(telegram_id, conf_name)
        if peer is None:
            logger.warning(
                "Peer with conf_name `%s` for telegram_id: %s does not exist",
                conf_name,
                telegram_id,
            )
            raise EntityNotExistsException(
                f"Peer with conf_name={conf_name} for User with telegram_id={telegram_id} does not exist"
            )
        switch_peer_active_status(telegram_id, conf_name, is_active)
        hc = HostClient(peer)
        try:
            if is_active:
                hc.activate_on_host()
                logger.info(
                    "Peer with conf_name `%s` for telegram_id: %s activated on host successfully",
                    conf_name,
                    telegram_id,
                )
            else:
                hc.deactivate_on_host()
                logger.info(
                    "Peer with conf_name `%s` for telegram_id: %s deactivated on host successfully",
                    conf_name,
                    telegram_id,
                )
        except Exception as exc:
            raise RuntimeError("Failed to switch peer from host") from exc

    @auto_transaction()
    def deactivate_all_peers(self, telegram_id: int) -> None:
        logger.info("Deactivating all peers for telegram_id: %s", telegram_id)
        peers = get_all_peers_by_user(telegram_id)
        for peer in peers:
            if peer.is_active:
                try:
                    switch_peer_active_status(telegram_id, peer.conf_name, False)
                except Exception as exc:
                    logger.error(
                        "Failed to deactivate peer %s for user %s: %s",
                        peer.conf_name,
                        telegram_id,
                        exc,
                    )
                    raise RuntimeError("Failed to deactivate all peers on host") from exc
        logger.info("All peers for telegram_id %s are deactivated", telegram_id)

    @auto_transaction()
    def delete_peer(self, telegram_id: int, conf_name: str) -> None:
        logger.info(
            "Deleting peer with telegram_id: %s and conf_name: %s",
            telegram_id,
            conf_name,
        )
        peer = get_peer(telegram_id, conf_name)
        if peer is None:
            logger.warning(
                "Peer with conf_name `%s` for telegram_id: %s does not exist",
                conf_name,
                telegram_id,
            )
            raise EntityNotExistsException(
                f"Peer with conf_name={conf_name} for User with telegram_id={telegram_id} does not exist"
            )
        delete_peer(telegram_id, conf_name)
        release_peer_ip(peer.host.id, peer.peer_ip)
        hc = HostClient(peer)
        try:
            hc.delete_peer_on_host()
            logger.info(
                "Peer with conf_name `%s` for telegram_id: %s deleted from host successfully",
                conf_name,
                telegram_id,
            )
        except Exception as exc:
            raise RuntimeError("Failed to delete peer from host") from exc

    @auto_transaction()
    def get_peer_download_token(self, telegram_id: int, conf_name: str) -> str:
        logger.info(
            "Getting download token for peer with telegram_id: %s and conf_name: %s",
            telegram_id,
            conf_name,
        )
        peer = get_peer(telegram_id, conf_name)
        if peer is None:
            logger.warning(
                "Peer with conf_name `%s` for telegram_id: %s does not exist",
                conf_name,
                telegram_id,
            )
            raise EntityNotExistsException(
                f"Peer with conf_name={conf_name} for User with telegram_id={telegram_id} does not exist"
            )
        hc = HostClient(peer)
        try:
            token = hc.get_download_conf_token()
            logger.info(
                "Download token for peer with conf_name `%s` for telegram_id: %s retrieved successfully",
                conf_name,
                telegram_id,
            )
            return token
        except Exception as exc:
            raise RuntimeError("Failed to get download token from host") from exc