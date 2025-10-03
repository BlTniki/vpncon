from typing import Any, LiteralString
import psycopg
from psycopg.cursor import Cursor
from psycopg import Connection
from psycopg.rows import TupleRow
from psycopg_pool import ConnectionPool

from ..config import Config
from .db import DBExecutor

# Глобальная переменная пула, но создаётся лениво
_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    """
    Возвращает пул соединений. Создаёт его при первом обращении.
    """
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=Config.DB_URI,
            min_size=Config.DB_POOL_MIN_SIZE,
            max_size=Config.DB_POOL_MAX_SIZE,
        )
    return _pool


def validate_connection(pool: ConnectionPool | None = None) -> None:
    """
    Проверяет, что можно выполнить простейший запрос к базе.
    Использует переданный пул или создаёт временное соединение.
    """
    if pool is not None:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result is None or result[0] != 1:
                    raise RuntimeError("Database connection validation failed.")
    else:
        # если пул ещё не создан — делаем временное подключение
        with psycopg.connect(Config.DB_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result is None or result[0] != 1:
                    raise RuntimeError("Database connection validation failed.")


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
        self.cur.execute(query, kwargs)
        if self.cur.description:
            return self.cur.fetchall()
        return []
