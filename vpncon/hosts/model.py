from sqlalchemy import Table, Column, BigInteger, String, Integer
from ..db import engine, metadata

hosts = Table(
    "hosts",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String),
    Column("ipaddres", String),
    Column("port", Integer),
    Column("host_password", String),
)
