from abc import ABC, abstractmethod
import logging

from vpncon.db import auto_transaction
from vpncon.db.db import UniqueConstraintError

from vpncon.exceptions import EntityAlreadyExistsException, EntityNotExistsException
from .crud import (
    create_host,
    get_host,
    update_host,
    delete_host,
    create_ip_pool_for_host,
    delete_ip_pool_for_host
)
from .model import Host

logger = logging.getLogger(__name__)


class HostService(ABC):

    @abstractmethod
    def create_host(
        self, host_id: int, name: str, ip_address: str, port: int, host_password: str
    ) -> None:
        pass

    @abstractmethod
    def get_host(self, host_id: int) -> Host | None:
        pass

    @abstractmethod
    def update_host(
        self, host_id: int, name: str, ip_address: str, port: int, host_password: str
    ) -> None:
        pass

    @abstractmethod
    def delete_host(self, host_id: int) -> None:
        pass


def build_ip_pool(subnet_prefix: str) -> list[str]:
    """Строит пул IP-адресов для хоста на основе префикса подсети.

    Args:
        subnet_prefix (str): Префикс подсети, например '10.8.0.'
    Returns:
        list[str]: Список IP-адресов для пула.
    Raises:
        ValueError: Если префикс подсети некорректен."""
    if not subnet_prefix.endswith("."):
        raise ValueError("subnet_prefix must end with '.' (e.g. '10.8.0.')")

    return [f"{subnet_prefix}{i}" for i in range(2, 255)]


class HostServiceCRUD(HostService):
    @auto_transaction()
    def create_host(
        self, host_id: int, name: str, ip_address: str, port: int, host_password: str
    ):
        logger.info("Creating host with id: %s", host_id)
        host = Host(host_id, name, ip_address, port, host_password)
        try:
            create_host(host)
        except UniqueConstraintError as exc:
            logger.warning("Failed to create host, already exists: %s", host_id)
            raise EntityAlreadyExistsException(
                f"Host with id={host_id} already exists"
            ) from exc

        # create ip pool for the host
        ip_pool = build_ip_pool("10.8.0.")
        create_ip_pool_for_host(host_id, ip_pool)

        logger.info("Host created successfully: %s", host_id)

    @auto_transaction()
    def get_host(self, host_id: int) -> Host | None:
        logger.debug("Retrieving host with id: %s", host_id)
        return get_host(host_id)

    @auto_transaction()
    def update_host(
        self, host_id: int, name: str, ip_address: str, port: int, host_password: str
    ) -> None:
        logger.info("Updating host with id: %s", host_id)
        if get_host(host_id) is None:
            logger.warning("Host not found for update: %s", host_id)
            raise EntityNotExistsException(f"Host with id={host_id} not found")
        host = Host(host_id, name, ip_address, port, host_password)
        update_host(host)
        logger.info("Host updated successfully: %s", host_id)

    @auto_transaction()
    def delete_host(self, host_id: int):
        logger.info("Deleting host with id: %s", host_id)
        if get_host(host_id) is None:
            logger.warning("Host not found for deletion: %s", host_id)
            raise EntityNotExistsException(f"Host with id={host_id} not found")
        delete_host(host_id)
        delete_ip_pool_for_host(host_id)
        logger.info("Host deleted successfully: %s", host_id)
