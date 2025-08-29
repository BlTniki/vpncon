from sqlalchemy import Table, Column, BigInteger, Float, Integer, Interval
from ..db import engine, metadata

subscriptions = Table(
    "subscriptions",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("price_in_rub", Float),
    Column("allowed_peers", Integer),
    Column("period", Interval),
)
