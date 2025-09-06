from abc import ABC, abstractmethod
from typing import Any, LiteralString
from psycopg.cursor import Cursor
from psycopg import Connection
from psycopg.rows import TupleRow
from psycopg_pool import ConnectionPool


class DBExecutor(ABC):
    @abstractmethod
    def execute(self, query: LiteralString, **kwargs: Any) -> list[tuple[Any, ...]]:
        """Executes a SQL query and returns the raw result as a list of tuples."""

    @abstractmethod
    def open(self) -> None:
        """Enter the runtime context related to this object."""

    @abstractmethod
    def close(self) -> None:
        """Exit the runtime context related to this object."""

class DBPool(ABC):
    @abstractmethod
    def get_conn(self) -> Any:
        """Get a connection from the pool."""
    @abstractmethod
    def put_conn(self, conn: Any) -> None:
        """Return a connection to the pool."""

class PostgresPool(DBPool):
    def __init__(self, db_uri: str, min_size: int = 1, max_size: int = 10) -> None:
        self.pool = ConnectionPool(db_uri, min_size=min_size, max_size=max_size)

    def get_conn(self) -> Any:
        return self.pool.getconn()

    def put_conn(self, conn: Any) -> None:
        self.pool.putconn(conn)


class PostgresExecutor(DBExecutor):
    def __init__(self, pool:PostgresPool, db_uri: str) -> None:
        self.db_uri = db_uri
        self.pool = pool
        self.conn:Connection[TupleRow]|None = None
        self.cur:Cursor[Any]|None = None

    def open(self) -> None:
        self.conn = self.pool.get_conn()
        self.cur = self.conn.cursor() # type: ignore

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.pool.put_conn(self.conn)
        self.conn = None
        self.cur = None

    def execute(self, query: LiteralString, **kwargs: Any) -> list[tuple[Any, ...]]:
        if not self.cur:
            raise RuntimeError("Connection is not open. Use 'with' statement.")
        self.cur.execute(query, kwargs)
        if self.cur.description:
            return self.cur.fetchall()
        return []
