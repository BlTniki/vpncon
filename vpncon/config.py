import logging
from logging import Formatter
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URI:str = os.getenv("DATABASE_URL")
    TELEGRAM_BOT_TOKEN:str = os.getenv("TELEGRAM_BOT_TOKEN")
    LOGGER_FORMAT:str = (os.getenv("LOGGER_FORMAT") or
        '%(asctime)s %(levelname)s: %(message)s [in %(name)s]'
    )
