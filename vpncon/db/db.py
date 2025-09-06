from abc import ABC, abstractmethod
from typing import Any, LiteralString
# docker run -d -p 5432:5432 --name vpncon -e POSTGRES_USER=vpncon -e POSTGRES_PASSWORD=123456 -d postgres:13.22-alpine3.22


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