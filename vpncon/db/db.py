from abc import ABC, abstractmethod
from typing import Any, LiteralString
import logging
# docker run -d -p 5432:5432 --name vpncon -e POSTGRES_USER=vpncon -e POSTGRES_PASSWORD=123456 -d postgres:13.22-alpine3.22

logger = logging.getLogger(__name__)

class DBExecutor(ABC):
    """Обёртка вокруг драйвера ДБ.
    Предоставляет абстрагированный от конкретной реализации драйвера функционал:
    - Управление соединением к ДБ (открытие, закрытие, использование пула)
    - Управление транзакциями

    Использование предполагает что на каждый поток один `DBExecutor`
    """
    @abstractmethod
    def open(self) -> None:
        """Открывает соединение и транзакцию. Позволяет вызывать `.execute()`.

        Если соединение уже открыто, то повторный вызов метода бросит исключение.
        Это делается для исключения повторного вызова метода во вложенной функции.
        `DBExecutor` не даёт гарантий, что если во вложенной функции
        будет вызван метод `.close()`, то он не закроет соединение на всех уровнях
        """

    @abstractmethod
    def close(self) -> None:
        """Закрывает соединение и коммитит транзакцию"""

    @abstractmethod
    def rollback_and_close(self) -> None:
        """Закрывает соединение и откатывает транзакцию"""

    @abstractmethod
    def execute(self, query: LiteralString, **kwargs: Any) -> list[tuple[Any, ...]]:
        """Выполняет переданный запрос с параметрами и возвращает ответ в виде списка кортежей.

        Перед вызовом метода необходимо открыть соединение, вызвав `.open()`
        """


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

