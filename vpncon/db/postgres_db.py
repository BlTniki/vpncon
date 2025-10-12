from typing import Any, LiteralString
import threading
import psycopg
import logging
from psycopg.cursor import Cursor
from psycopg import Connection
from psycopg.rows import TupleRow
from psycopg_pool import ConnectionPool

from ..config import Config
from .db import DBExecutor, UniqueConstraintError

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None
_pool_lock = threading.Lock()

def get_pool() -> ConnectionPool:
    """ Возвращает пул соединений. Создаёт его при первом обращении.

    Потокобезопасный. Разделяет общий пул на все потоки
    """
    global _pool
    if _pool is None:                        # быстрая проверка без блокировки
        with _pool_lock:                      # блокируем создание
            if _pool is None:                 # повторная проверка (double-checked locking)
                _pool = ConnectionPool(
                    conninfo=Config.DB_URI,
                    min_size=Config.DB_POOL_MIN_SIZE,
                    max_size=Config.DB_POOL_MAX_SIZE,
                )
    return _pool


def validate_connection() -> None:
    """
    Проверяет, что можно выполнить простейший запрос к базе.
    Создаёт временное соединение с таймаутом 20 секунд
    """
    logger.debug("Trying to connect to the database...")
    with psycopg.connect(Config.DB_URI, connect_timeout=20) as conn:
        logger.debug("Connection to the database established.")
        with conn.cursor() as cur:
            logger.debug("Executing test query...")
            cur.execute("SELECT 1")
            result = cur.fetchone()
            if result is None or result[0] != 1:
                raise RuntimeError("Database connection validation failed.")
    logger.debug("Database connection validated successfully")


class PostgresExecutor(DBExecutor):
    """Реализация `DBExecutor` для работы с postgres.
    Более подробное описание назначения можно увидеть в `DBExecutor`
    """
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool = pool
        self.conn: Connection[TupleRow] | None = None
        self.cur: Cursor[TupleRow] | None = None

    def open(self) -> None:
        if self.conn:
            raise RuntimeError(
                "Incorrect use: repeated .open() method"
                + " invocation when the connection is already open"
            )
        self.conn = self.pool.getconn()
        self.cur = self.conn.cursor()  # type: ignore

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.pool.putconn(self.conn)
        self.conn = None
        self.cur = None


    def commit_and_close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.commit()
            self.pool.putconn(self.conn)
        self.conn = None
        self.cur = None

    def rollback_and_close(self) -> None:
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.rollback()
            self.pool.putconn(self.conn)
        self.conn = None
        self.cur = None

    def execute(self, query: LiteralString, **kwargs: Any) -> list[tuple[Any, ...]]:
        if not self.conn or not self.cur:
            raise RuntimeError("Connection is not open. Use 'open()' method first.")
        try:
            self.cur.execute(query, kwargs)
            if self.cur.description:
                return self.cur.fetchall()
            return []
        except Exception as exc:
            # Абстрагированная проверка по имени класса
            if exc.__class__.__name__ == "IntegrityError":
                raise UniqueConstraintError() from exc
            raise
