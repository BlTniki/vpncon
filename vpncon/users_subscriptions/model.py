from sqlalchemy import Table, Column, BigInteger, Date
from ..db import engine, metadata

users_subscriptions = Table(
    "users_subscriptions",
    metadata,
    Column("user_id", BigInteger, primary_key=True),
    Column("subscription_id", BigInteger),
    Column("expiration_date", Date),
)
