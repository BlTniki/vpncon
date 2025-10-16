"""
Базовая миграция для создания таблицы версий схемы БД.
"""

script = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR PRIMARY KEY,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""
