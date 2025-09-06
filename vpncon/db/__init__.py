from ..config import Config
from .db import DBExecutor
from .postgres_db import PostgresExecutor, get_pool

pool = get_pool()
db_executor:DBExecutor = PostgresExecutor(pool)

