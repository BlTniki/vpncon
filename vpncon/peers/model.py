from sqlalchemy import Table, Column, BigInteger, String, Boolean
from ..db import engine, metadata

peers = Table(
    "peers",
    metadata,
    Column("user_id", BigInteger, primary_key=True),
    Column("host_id", BigInteger, primary_key=True),
    Column("conf_name", String),
    Column("peer_ip", String),
    Column("is_activated", Boolean),
)
