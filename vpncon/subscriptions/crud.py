from .model import subscriptions
from sqlalchemy.sql import select, insert, update, delete
from ..db import engine

def get_subscription(sub_id):
    with engine.connect() as conn:
        stmt = select(subscriptions).where(subscriptions.c.id == sub_id)
        result = conn.execute(stmt).fetchone()
        return dict(result) if result else None

def create_subscription(id, price_in_rub, allowed_peers, period):
    with engine.connect() as conn:
        stmt = insert(subscriptions).values(id=id, price_in_rub=price_in_rub, allowed_peers=allowed_peers, period=period)
        conn.execute(stmt)
        conn.commit()

def update_subscription(id, **fields):
    with engine.connect() as conn:
        stmt = update(subscriptions).where(subscriptions.c.id == id).values(**fields)
        conn.execute(stmt)
        conn.commit()

def delete_subscription(id):
    with engine.connect() as conn:
        stmt = delete(subscriptions).where(subscriptions.c.id == id)
        conn.execute(stmt)
        conn.commit()

def list_subscriptions():
    with engine.connect() as conn:
        stmt = select(subscriptions)
        result = conn.execute(stmt).fetchall()
        return [dict(row) for row in result]
