from abc import ABC, abstractmethod
from typing import Any, LiteralString
import logging
import psycopg

from vpncon.config import Config

from .migrations import *


logger = logging.getLogger(__name__)





# SQL экзекьютор для выполнения миграций и валидации схемы БД
class MigrationExecutor(ABC):
    """Обёртка вокруг драйвера БД. Используется только для миграций и валидации схемы БД.
    Не предоставляет управление транзакциями,
    подключение открывается и закрывается для каждого запроса.
    """
    @abstractmethod
    @staticmethod
    def execute(queries: list[LiteralString], **kwargs: Any) -> list[list[tuple[Any, ...]]]:
        """Выполняет переданные запросы с параметрами
          и возвращает ответ в виде списка списка кортежей."""


class PostgresMigrationExecutor(MigrationExecutor):
    """Реализация `MigrationExecutor` для работы с postgres.
    Более подробное описание назначения можно увидеть в `MigrationExecutor`
    """

    @staticmethod
    def execute(queries: list[LiteralString], **kwargs: Any) -> list[list[tuple[Any, ...]]]:
        logger.debug("Opening new connection for migration executor")
        with psycopg.connect(Config.DB_URI, connect_timeout=20) as conn:
            logger.debug("Connection opened")
            with conn.cursor() as cur:
                results = []
                for query in queries:
                    logger.debug("Executing query: %s", query)
                    cur.execute(query, kwargs)
                    if cur.description:
                        results.append(cur.fetchall())
                    else:
                        results.append([])
        return results


class DbMigration:
    """Класс для управления миграциями и валидацией схемы БД.
    Использует `MigrationExecutor` для выполнения запросов.
    """
    def __init__(self, executor: MigrationExecutor) -> None:
        self.executor = executor


    # Установщик миграций
    def apply_migrations(self) -> None:
        """
        Сверяет текущую версию схемы БД с версиями миграций, приставленных в `.migrations`.
        Если текущая версия меньше, чем последняя миграция, применяет все необходимые миграции
        """
        # 1. Получить список миграций
        import os
        import importlib
        migrations_dir = os.path.dirname(__file__) + '/migrations'
        migration_files = [f for f in os.listdir(migrations_dir) if f.startswith('M_') and f.endswith('.py')]
        migration_files.sort()
        migrations = []
        for fname in migration_files:
            mod_name = f'.migrations.{fname[:-3]}'
            mod = importlib.import_module(mod_name, package=__package__)
            migrations.append(mod)

        # 2. Проверить наличие таблицы schema_migrations
        table_name = getattr(migrations[0], 'migrations_table_name', 'schema_migrations')
        check_table_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            )
        """
        table_exists = self.executor.execute(check_table_query)
        if not table_exists or not table_exists[0][0]:
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