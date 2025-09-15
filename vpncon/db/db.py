from abc import ABC, abstractmethod
from typing import Any, LiteralString
import logging
# docker run -d -p 5432:5432 --name vpncon -e POSTGRES_USER=vpncon -e POSTGRES_PASSWORD=123456 -d postgres:13.22-alpine3.22

logger = logging.getLogger(__name__)

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


def auto_transaction(func):
    """Инициализирует подключение и транзакцию.
    Транзакция открывается на входе в приложение

    Args:
        func (_type_): _description_
    """
    def wrapper(*args, **kwargs):
        _proxy.init()
        result = f(*args, **kwargs)
        _proxy.kill()
        return result
    return wrapper

