from typing import Any, LiteralString
import psycopg
from psycopg.cursor import Cursor
from psycopg import Connection
from psycopg.rows import TupleRow
from psycopg_pool import ConnectionPool

from ..config import Config
from .db import DBExecutor


def get_pool() -> ConnectionPool:
    return ConnectionPool(
        Config.DB_URI,
        min_size=Config.DB_POOL_MIN_SIZE,
        max_size=Config.DB_POOL_MAX_SIZE
    )

def validate_connection() -> None:
    with psycopg.connect(Config.DB_URI) as conn:
        with conn.cursor() as cur:
            # Simple query to validate the connection
            cur.execute("SELECT 1")
            result = cur.fetchone()
            if result is None or result[0] != 1:
                raise RuntimeError("Database connection validation failed.")

class PostgresExecutor(DBExecutor):
    def __init__(self, pool:ConnectionPool) -> None:
        self.pool = pool
        self.conn:Connection[TupleRow]|None = None
        self.cur:Cursor[TupleRow]|None = None

    def open(self) -> None:
        self.conn = self.pool.getconn()
        self.cur = self.conn.cursor() # type: ignore

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.pool.putconn(self.conn)
        self.conn = None
        self.cur = None

    def execute(self, query: LiteralString, **kwargs: Any) -> list[tuple[Any, ...]]:
        if not self.cur:
            raise RuntimeError("Connection is not open. Use 'with' statement.")
        self.cur.execute(query, kwargs)
        if self.cur.description:
            return self.cur.fetchall()
        return []
