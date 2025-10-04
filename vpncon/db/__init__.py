import threading
import weakref
import logging
from .db import DBExecutor
from .postgres_db import PostgresExecutor, get_pool, validate_connection

logger = logging.getLogger(__name__)

logger.info("Initializing the DB module")


validate_connection()
logger.debug("Connection validated")



_thread_local = threading.local()

def _create_executor() -> DBExecutor:
    """Создаёт `DBExecutor` и вешает на него хук для его закрытия перед удалением Garbage Collector
    """
    executor = PostgresExecutor(get_pool())
    # Освободить ресурсы при уничтожении объекта
    # Думаю это можно назвать хуком, который будет вызван сборщиком мусора
    weakref.finalize(executor, executor.close)
    return executor

def get_db_executor() -> DBExecutor:
    """Возвращает `DBExecutor` для конкретного потока.
    Инициализирует `DBExecutor`, если он еще создан для потока
    """
    if not hasattr(_thread_local, "executor"):
        _thread_local.executor = _create_executor()
    return _thread_local.executor

def auto_transaction(func):
    """Инициализирует подключение и транзакцию.
    Транзакция открывается на входе в приложение

    Args:
        func (_type_): _description_
    """
    # 
    def wrapper(*args, **kwargs):
        _proxy.init()
        result = f(*args, **kwargs)
        _proxy.kill()
        return result
    return wrapper