import psycopg
from psycopg import Que
from abc import ABC, abstractmethod


class DBExecutor(ABC):
    @abstractmethod
    def execute(self, query: str) -> list[tuple]:
        """Executes a SQL query with optional parameters and returns the result as a list of tuples."""


class PostgresExecutor(DBExecutor):
    def __init__(self, db_uri: str) -> None:
        self.db_uri = db_uri

        # Test connection
        with psycopg.connect(self.db_uri) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")

    def execute(self, query: str) -> list[tuple]:
        with psycopg.connect(self.db_uri) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description:  # Check if the query returns rows
                    return cur.fetchall()
                return []
