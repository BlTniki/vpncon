

scripts = ["""
CREATE TABLE IF NOT EXISTS users (
    telegram_id BIGINT PRIMARY KEY,
    telegram_nick VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL
);
"""]