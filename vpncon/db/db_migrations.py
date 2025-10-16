from abc import ABC, abstractmethod
from typing import Any, LiteralString
import logging
import psycopg
import os
import importlib

from vpncon.config import Config


logger = logging.getLogger(__name__)





# SQL экзекьютор для выполнения миграций и валидации схемы БД
class MigrationExecutor(ABC):
    """Обёртка вокруг драйвера БД. Используется только для миграций и валидации схемы БД.
    Не предоставляет управление транзакциями,
    подключение открывается и закрывается для каждого запроса.
    """
    @abstractmethod
    @staticmethod
    def execute(query: LiteralString, **kwargs: Any) -> list[tuple[Any, ...]]:
        """Выполняет переданные запросы с параметрами
          и возвращает ответ в виде списка списка кортежей."""


class PostgresMigrationExecutor(MigrationExecutor):
    """Реализация `MigrationExecutor` для работы с postgres.
    Более подробное описание назначения можно увидеть в `MigrationExecutor`
    """

    @staticmethod
    def execute(query: LiteralString, **kwargs: Any) -> list[tuple[Any, ...]]:
        logger.debug("Opening new connection for migration executor")
        with psycopg.connect(Config.DB_URI, connect_timeout=20) as conn:
            logger.debug("Connection opened")
            with conn.cursor() as cur:
                logger.debug("Executing query: %s", query)
                cur.execute(query, kwargs)
                if cur.description:
                    return cur.fetchall()
                else:
                    return []


class DbMigration:
    """Класс для управления миграциями и валидацией схемы БД.
    Использует `MigrationExecutor` для выполнения запросов.
    """
    def __init__(self, executor: MigrationExecutor) -> None:
        self.executor = executor

    def _load_migrations(self) -> list[tuple[str, str]]:
        """Загружает список миграций из папки `migrations` в формате
        [('M_0000_init_schema_migrations', 'CREATE TABLE ...'), ...]
        """
        migrations_dir = os.path.dirname(__file__) + '/migrations'
        logger.debug("Loading migrations from directory: %s", migrations_dir)
        migration_files = [
            f for f in os.listdir(migrations_dir) if f.startswith('M_') and f.endswith('.py')
        ]
        migration_files.sort()
        migrations:list[tuple[str, str]] = []
        for fname in migration_files:
            mod_name = f'.migrations.{fname[:-3]}'
            mod = importlib.import_module(mod_name, package=__package__)
            if hasattr(mod, 'script'):
                migrations.append((fname[:6], mod.script))
        return migrations

    def _update_version_in_schema_migrations(self, version: str) -> None:
        """Обновляет текущую версию схемы в таблице schema_migrations
        """
        insert_query = """
            INSERT INTO schema_migrations (version)
            VALUES (%(version)s)
            ON CONFLICT (version) DO NOTHING
        """
        self.executor.execute(insert_query, version=version)

    def apply_migrations(self) -> None:
        """
        Сверяет текущую версию схемы БД с версиями миграций, приставленных в `.migrations`.
        Если текущая версия меньше, чем последняя миграция, применяет все необходимые миграции
        """
        # 1. Получить список миграций
        migrations = self._load_migrations()
        if not migrations or migrations[0][0] != 'M_0000_init_schema_migrations':
            logger.fatal(
                "Migration directory is empty or missing the initial migration." \
                " There must be at least the M_0000_init_schema_migrations migration."
            )
            raise RuntimeError("No migrations found.")

        # 2. Определяем текущую версию схемы
        table_name = 'schema_migrations'
        check_table_query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '(%(table_name)s)'
            )
        """
        table_exists = self.executor.execute(check_table_query, table_name=table_name)
        if not table_exists or not table_exists[0][0]:
            logger.info("Schema migrations table does not exist. Creating it.")
            # Применить первую миграцию для создания таблицы
            if hasattr(migrations[0], 'upgrade'):
                migrations[0].upgrade(self.executor)

        # 3. Получить текущую версию схемы
        get_version_query = f"SELECT max(version) FROM {table_name}"
        version_result = self.executor.execute(get_version_query)
        current_version = version_result[0][0] if version_result and version_result[0][0] is not None else 0

        # 4. Применить недостающие миграции
        for idx, migration in enumerate(migrations):
            migration_version = idx
            if migration_version > current_version:
                if hasattr(migration, 'upgrade'):
                    migration.upgrade(self.executor)