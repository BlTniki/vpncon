# vpncon

VPN control system with Flask REST API, PostgreSQL, SQLAlchemy Core, Alembic, and Telegram bot.

## Основные модули
- Flask REST API
- PostgreSQL (psycopg2)
- SQLAlchemy Core (без ORM)
- Alembic (миграции)
- Telegram Bot (в будущем)

## Быстрый старт

1. Установите зависимости:
	```sh
	pip install poetry
	poetry install
	```
2. Скопируйте `.env.example` в `.env` и укажите свои параметры.
3. Инициализируйте базу данных и примените миграции Alembic.
4. Запустите приложение:
	```sh
	poetry run python -m vpncon.app
	```

## Структура
- `vpncon/` — основной код приложения
- `alembic/` — миграции Alembic
- `.env.example` — пример переменных окружения

## users
Модуль users реализует CRUD для пользователей (см. ER-диаграмму в документации).
"# vpncon" 
