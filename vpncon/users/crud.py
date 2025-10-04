from typing import Any
from .model import users
from ..db import _db_executor

def get_user(telegram_id:int) -> Row[Any] | None:
    with engine.connect() as conn:
        stmt = select(users).where(users.c.telegram_id == telegram_id)
        result:Row[Any] | None = conn.execute(stmt).fetchone()
        return result

# def create_user(telegram_id:int, telegram_nick:str, role:str):
#     with engine.connect() as conn:
#         stmt = insert(users).values(telegram_id=telegram_id, telegram_nick=telegram_nick, role=role)
#         conn.execute(stmt)
#         conn.commit()

# def update_user(telegram_id:int, **fields:Any):
#     with engine.connect() as conn:
#         stmt = update(users).where(users.c.telegram_id == telegram_id).values(**fields)
#         conn.execute(stmt)
#         conn.commit()

# def delete_user(telegram_id: int):
#     with engine.connect() as conn:
#         stmt = delete(users).where(users.c.telegram_id == telegram_id)
#         conn.execute(stmt)
#         conn.commit()