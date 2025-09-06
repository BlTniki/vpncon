import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LOGGER_FORMAT:str = (os.getenv("LOGGER_FORMAT") or
        '%(asctime)s %(levelname)s: %(message)s [in %(name)s]'
    )

    DB_URI:str = os.getenv("DATABASE_URL") or ""
    DB_POOL_MIN_SIZE:int = int(os.getenv("DB_POOL_MIN_SIZE") or 1)
    DB_POOL_MAX_SIZE:int = int(os.getenv("DB_POOL_MAX_SIZE") or 10)

    TELEGRAM_BOT_TOKEN:str = os.getenv("TELEGRAM_BOT_TOKEN") or ""
