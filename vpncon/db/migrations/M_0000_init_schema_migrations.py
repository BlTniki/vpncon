"""
Базовая миграция для создания таблицы версий схемы БД.
"""

scripts = ["""
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""]
