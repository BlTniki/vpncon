import logging
from .db import DBExecutor
from .postgres_db import PostgresExecutor, get_pool, validate_connection

logger = logging.getLogger(__name__)

logger.info("Initializing the DB module")

# ❗️ Убираем создание пула на этапе импорта
# ❗️ validate_connection() можно оставить для проверки доступности БД
#    но выполнять её будем лениво при первом запросе пула
validate_connection()
logger.debug("Connection validated")


db_executor: DBExecutor | None = None  # будет создан при первом доступе

def get_db_executor() -> DBExecutor:
    """
    Возвращает готовый DBExecutor.
    Если еще не создан, лениво создаёт пул и executor.
    """
    global db_executor
    if db_executor is None:
        logger.debug("Lazy initializing DBExecutor")
        pool = get_pool()                 # создаём пул в воркере
        validate_connection(pool)         # проверяем соединение
        db_executor = PostgresExecutor(pool)
        logger.info("DBExecutor initialized")
    return db_executor