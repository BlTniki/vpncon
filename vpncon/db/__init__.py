import logging

from .db import DBExecutor
from .postgres_db import PostgresExecutor, get_pool, validate_connection

logger = logging.getLogger(__name__)

logger.debug("Initializing the DB")

validate_connection()
logger.debug("Connection validated")
pool = get_pool()
logger.debug("Connection pool initialized")

db_executor:DBExecutor = PostgresExecutor(pool)
logger.debug("DBExecutor initialized")


logger.info("DB initialized")

