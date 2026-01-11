import logging
from typing import Any
from vpncon.db import auto_transaction, get_db_executor, UniqueConstraintError
from .model import Host

logger = logging.getLogger(__name__)


@auto_transaction()
def get_host(host_id: int) -> Host | None:
    """Получает хост по его id.
    Args:
        host_id (int): Идентификатор хоста.
    Returns:
        Host | None: Экземпляр Host, если хост найден, иначе None.
    """
    executor = get_db_executor()

    query = f"""
        SELECT
            {Host.get_model_fields_joined()}
        FROM hosts WHERE id = %(host_id)s
    """
    params: dict[str, Any] = {
        'host_id': host_id
    }
    result = executor.execute(query, **params)
    if not result:
        return None
    if len(result) > 1:
        raise ValueError(f"Multiple hosts found with id={host_id}")
    logger.debug("Host found: %s", result)
    return Host.from_raw(result[0])


@auto_transaction()
def create_host(host: Host) -> None:
    """Создаёт новый хост.
    Если хост с таким id уже существует, бросает исключение.
    Args:
        host (Host): Экземпляр хоста для создания.
    """
    executor = get_db_executor()
    query = f"""
        INSERT INTO hosts ({Host.get_model_fields_joined()})
        VALUES (%(id)s, %(name)s, %(ip_address)s, %(port)s, %(host_password)s)
    """
    params: dict[str, Any] = {
        'id': host.id,
        'name': host.name,
        'ip_address': host.ip_address,
        'port': host.port,
        'host_password': host.host_password
    }
    try:
        executor.execute(query, **params)
        logger.info("Host created: %s", host.id)
    except UniqueConstraintError as exc:
        raise UniqueConstraintError(
            f"Host with id={host.id} already exists"
        ) from exc


@auto_transaction()
def update_host(host: Host) -> None:
    """Обновляет данные хоста.
    Args:
        host (Host): Экземпляр хоста с обновлёнными данными.
    """
    executor = get_db_executor()
    query = """
        UPDATE hosts
        SET name = %(name)s,
            ip_address = %(ip_address)s,
            port = %(port)s,
            host_password = %(host_password)s
        WHERE id = %(id)s
    """
    params: dict[str, Any] = {
        'id': host.id,
        'name': host.name,
        'ip_address': host.ip_address,
        'port': host.port,
        'host_password': host.host_password
    }
    executor.execute(query, **params)
    logger.info("Host updated: %s", host.id)


@auto_transaction()
def delete_host(host_id: int) -> None:
    """Удаляет хост по его id.
    Args:
        host_id (int): Идентификатор хоста.
    """
    executor = get_db_executor()
    query = """
        DELETE FROM hosts WHERE id = %(host_id)s
    """
    params: dict[str, Any] = {
        'host_id': host_id
    }
    executor.execute(query, **params)
    logger.info("Host deleted: %s", host_id)


@auto_transaction()
def create_ip_pool_for_host(host_id: int, ip_list: list[str]) -> None:
    """Создаёт пул IP-адресов для хоста.
    Args:
        host_id (int): Идентификатор хоста.
        ip_list (list[str]): Список IP-адресов для пула.
    """
    executor = get_db_executor()

    # Batch insert IPs into the pool
    batch_inserts: list[str] = []
    for ip in ip_list:
        batch_inserts.append(f"({host_id}, '{ip}', false)")
    query = f"""
        INSERT INTO host_ip_pool (host_id, peer_ip, is_used)
        VALUES
            {', '.join(batch_inserts)}
    """
    try:
        executor.execute(query) # type: ignore
    except UniqueConstraintError as exc:
        raise UniqueConstraintError(
            f"IP pool for host_id={host_id} already exists"
        ) from exc

    logger.info("IP pool created for host: %s", host_id)


@auto_transaction()
def delete_ip_pool_for_host(host_id: int) -> None:
    """Удаляет пул IP-адресов для хоста.
    Args:
        host_id (int): Идентификатор хоста.
    """
    executor = get_db_executor()
    query = """
        DELETE FROM host_ip_pool WHERE host_id = %(host_id)s
    """
    params: dict[str, Any] = {
        'host_id': host_id
    }
    executor.execute(query, **params)
    logger.info("IP pool deleted for host: %s", host_id)


@auto_transaction()
def get_ip_pool_for_host(host_id: int) -> list[str]:
    """Получает пул IP-адресов для хоста.
    Args:
        host_id (int): Идентификатор хоста.
    Returns:
        list[str]: Список IP-адресов в пуле.
    """
    executor = get_db_executor()
    query = """
        SELECT peer_ip FROM host_ip_pool WHERE host_id = %(host_id)s ORDER BY peer_ip
    """
    params: dict[str, Any] = {
        'host_id': host_id
    }
    result = executor.execute(query, **params)
    return [row[0] for row in result]

