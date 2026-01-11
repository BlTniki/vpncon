import logging
from typing import Any
from vpncon.db import auto_transaction, get_db_executor, UniqueConstraintError
from .model import Peer

logger = logging.getLogger(__name__)


@auto_transaction()
def get_peer(telegram_id: int, conf_name: str) -> Peer | None:
    """Получает пира пользователя по его telegram_id и названию пира.
    Args:
        telegram_id (int): Идентификатор пользователя в Telegram.
        conf_name (str): Имя конфигурации.
    Returns:
        Peer | None: Экземпляр Peer, если пир найден, иначе None.
    """
    executor = get_db_executor()

    query = """
        SELECT
            u.*,
            h.*,
            p.conf_name,
            p.peer_ip,
            p.is_active
        FROM peers p
        JOIN users u ON u.telegram_id = p.user_id
        JOIN hosts h ON h.id = p.host_id
        WHERE p.user_id = %(telegram_id)s AND p.conf_name = %(conf_name)s
    """
    params: dict[str, Any] = {"telegram_id": telegram_id, "conf_name": conf_name}
    result = executor.execute(query, **params)
    if not result:
        return None
    if len(result) > 1:
        raise ValueError(
            f"Multiple peers found with telegram_id={telegram_id} and conf_name={conf_name}"
        )
    logger.debug("Peer found: %s", result)
    return Peer.from_raw(result[0])


def get_all_peers_by_user(telegram_id: int) -> list[Peer]:
    """Получает всех пиров пользователя по его telegram_id.
    Args:
        telegram_id (int): Идентификатор пользователя в Telegram.
    Returns:
        list[Peer]: Список экземпляров Peer.
    """
    executor = get_db_executor()

    query = """
        SELECT
            u.*,
            h.*,
            p.conf_name,
            p.peer_ip,
            p.is_active
        FROM peers p
        JOIN users u ON u.telegram_id = p.user_id
        JOIN hosts h ON h.id = p.host_id
        WHERE p.user_id = %(telegram_id)s
    """
    params: dict[str, Any] = {"telegram_id": telegram_id}
    result = executor.execute(query, **params)
    logger.debug("Peers found for user %s: %s", telegram_id, result)
    return [Peer.from_raw(row) for row in result]


@auto_transaction()
def pick_and_lock_peer_ip(host_id: int) -> str|None:
    """Выбирает и блокирует свободный IP-адрес для пира на указанном хосте.
    Возвращает None, если свободных IP-адресов нет.
    Args:
        host_id (int): Идентификатор хоста.
    Returns:
        str: Выбранный IP-адрес.
        None: Если свободных IP-адресов нет.
    """
    executor = get_db_executor()

    query = """
        UPDATE host_ip_pool
        SET is_used = true
        WHERE (host_id, peer_ip) = (
            SELECT host_id, peer_ip
            FROM host_ip_pool
            WHERE host_id = %(host_id)s AND is_used = false
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        )
        RETURNING peer_ip
    """
    params: dict[str, Any] = {"host_id": host_id}
    result = executor.execute(query, **params)
    if not result:
        return None
    selected_ip = result[0][0]
    logger.info("Picked and locked IP %s for host_id=%s", selected_ip, host_id)
    return selected_ip


@auto_transaction()
def release_peer_ip(host_id: int, peer_ip: str) -> None:
    """Освобождает IP-адрес пира на указанном хосте.
    Args:
        host_id (int): Идентификатор хоста.
        peer_ip (str): IP-адрес пира.
    """
    executor = get_db_executor()
    query = """
        UPDATE host_ip_pool
        SET is_used = false
        WHERE host_id = %(host_id)s AND peer_ip = %(peer_ip)s
    """
    params: dict[str, Any] = {"host_id": host_id, "peer_ip": peer_ip}
    executor.execute(query, **params)
    logger.info("Released IP %s for host_id=%s", peer_ip, host_id)


@auto_transaction()
def create_peer(
    user_id: int, host_id: int, conf_name: str, peer_ip: str
) -> None:
    """Создаёт нового пира пользователю.
    Если у пользователя уже существует пир с таким названием, то бросает исключение.
    Также бросает исключение, если указанный IP адрес уже занят на данном хосте.
    Args:
        user_id (int): Идентификатор пользователя в Telegram.
        host_id (int): Идентификатор хоста.
        conf_name (str): Имя конфигурации.
        peer_ip (str): IP-адрес пира.
    """

    executor = get_db_executor()
    query = """
        INSERT INTO peers (user_id, host_id, conf_name, peer_ip, is_active)
        VALUES (%(user_id)s, %(host_id)s, %(conf_name)s, %(peer_ip)s, true)
    """
    params: dict[str, Any] = {
        "user_id": user_id,
        "host_id": host_id,
        "conf_name": conf_name,
        "peer_ip": peer_ip
    }
    try:
        executor.execute(query, **params)
        logger.info(
            "Peer created: %s, %s, %s",
            user_id,
            host_id,
            conf_name,
        )
    except UniqueConstraintError as exc:
        # Абстрагированная проверка по имени класса
        raise UniqueConstraintError(
            f"Peer with conf_name={conf_name} for User with telegram_id={user_id}" + "already exists"
        ) from exc


@auto_transaction()
def delete_peer(user_id: int, conf_name: str) -> None:
    """Удаляет подписку пользователя по его telegram_id и названию пира.

    Args:
        user_id (int): Идентификатор пользователя в Telegram.
        conf_name (str): Имя конфигурации.
    """
    executor = get_db_executor()
    query = """
        DELETE FROM peers WHERE user_id = %(user_id)s AND conf_name = %(conf_name)s
    """
    params: dict[str, Any] = {"user_id": user_id, "conf_name": conf_name}
    executor.execute(query, **params)
    logger.info("Peer deleted: %s, %s", user_id, conf_name)


@auto_transaction()
def switch_peer_active_status(
    user_id: int, conf_name: str, is_active: bool
) -> None:
    """Переключает статус активности пира пользователя.

    Args:
        user_id (int): Идентификатор пользователя в Telegram.
        conf_name (str): Имя конфигурации.
        is_active (bool): Новый статус активности.
    """
    executor = get_db_executor()
    query = """
        UPDATE peers
        SET is_active = %(is_active)s
        WHERE user_id = %(user_id)s AND conf_name = %(conf_name)s
    """
    params: dict[str, Any] = {
        "user_id": user_id,
        "conf_name": conf_name,
        "is_active": is_active,
    }
    executor.execute(query, **params)
    logger.info(
        "Peer active status switched: %s, %s, %s",
        user_id,
        conf_name,
        is_active,
    )