import os
import logging.config
import yaml
from dotenv import load_dotenv
from typing import Any

load_dotenv()

class Config:
    DB_URI:str = os.getenv("DB_URI") or ""
    DB_POOL_MIN_SIZE:int = int(os.getenv("DB_POOL_MIN_SIZE") or 1)
    DB_POOL_MAX_SIZE:int = int(os.getenv("DB_POOL_MAX_SIZE") or 5)

    TELEGRAM_BOT_TOKEN:str = os.getenv("TELEGRAM_BOT_TOKEN") or ""




def setup_logging(
    default_path:str="logging.yml",
    default_level:str="INFO",
):
    """
    Настройка логирования через logging.yml и .env

    Поддержка .env:
      LOG_LEVEL=DEBUG
      LOG_LEVELS=myapp.db=INFO,myapp.services.auth=ERROR
    """
    # root уровень
    root_level = os.getenv("LOG_LEVEL", default_level)

    # Таргетированные уровни
    raw_levels = os.getenv("LOG_LEVELS", "")
    overrides:dict[str, str] = {}
    for pair in raw_levels.split(","):
        if "=" in pair:
            name, level = pair.split("=", 1)
            overrides[name.strip()] = level.strip()

    # Загружаем logging.yml
    if os.path.exists(default_path):
        with open('logging.yml', 'r', encoding='utf-8') as f:
            config:dict[str, Any] = yaml.safe_load(f)
    else:
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "root": {"level": root_level, "handlers": ["console"]},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                }
            },
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
        }

    # Применяем root
    config["root"]["level"] = root_level

    # Применяем overrides
    if overrides:
        if "loggers" not in config:
            config["loggers"] = {}
        for logger_name, level in overrides.items():
            if logger_name not in config["loggers"]:
                config["loggers"][logger_name] = {"handlers": [], "propagate": True}
            config["loggers"][logger_name]["level"] = level

    logging.config.dictConfig(config)
