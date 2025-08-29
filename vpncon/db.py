from sqlalchemy import create_engine, MetaData, Engine
from .config import Config

engine:Engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, future=True) # type: ignore
metadata = MetaData()
