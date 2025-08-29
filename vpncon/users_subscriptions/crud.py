from .model import users_subscriptions
from sqlalchemy.sql import select, insert, update, delete
from ..db import engine

def get_user_subscription(user_id):
    with engine.connect() as conn:
        stmt = select(users_subscriptions).where(users_subscriptions.c.user_id == user_id)
        result = conn.execute(stmt).fetchone()
        return dict(result) if result else None

def create_user_subscription(user_id, subscription_id, expiration_date):
    with engine.connect() as conn:
        stmt = insert(users_subscriptions).values(user_id=user_id, subscription_id=subscription_id, expiration_date=expiration_date)
        conn.execute(stmt)
        conn.commit()

def update_user_subscription(user_id, **fields):
    with engine.connect() as conn:
        stmt = update(users_subscriptions).where(users_subscriptions.c.user_id == user_id).values(**fields)
        conn.execute(stmt)
        conn.commit()

def delete_user_subscription(user_id):
    with engine.connect() as conn:
        stmt = delete(users_subscriptions).where(users_subscriptions.c.user_id == user_id)
        conn.execute(stmt)
        conn.commit()

def list_users_subscriptions():
    with engine.connect() as conn:
        stmt = select(users_subscriptions)
        result = conn.execute(stmt).fetchall()
        return [dict(row) for row in result]
