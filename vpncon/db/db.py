from abc import ABC, abstractmethod
from typing import Any, LiteralString
import logging


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
        """Закрывает соединение"""

    @abstractmethod
    def commit_and_close(self) -> None:
        """Закрывает соединение и коммитит транзакцию"""

    @abstractmethod
    def rollback_and_close(self) -> None:
        """Закрывает соединение и откатывает транзакцию"""

    @abstractmethod
    def execute(self, query: LiteralString, **kwargs: Any) -> list[tuple[Any, ...]]:
        """Выполняет переданный запрос с параметрами и возвращает ответ в виде списка кортежей.

        Перед вызовом метода необходимо открыть соединение, вызвав `.open()`
        """
