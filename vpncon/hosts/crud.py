from .model import hosts
from sqlalchemy.sql import select, insert, update, delete
from ..db import engine

def get_host(host_id):
    with engine.connect() as conn:
        stmt = select(hosts).where(hosts.c.id == host_id)
        result = conn.execute(stmt).fetchone()
        return dict(result) if result else None

def create_host(id, name, ipaddres, port, host_password):
    with engine.connect() as conn:
        stmt = insert(hosts).values(id=id, name=name, ipaddres=ipaddres, port=port, host_password=host_password)
        conn.execute(stmt)
        conn.commit()

def update_host(id, **fields):
    with engine.connect() as conn:
        stmt = update(hosts).where(hosts.c.id == id).values(**fields)
        conn.execute(stmt)
        conn.commit()

def delete_host(id):
    with engine.connect() as conn:
        stmt = delete(hosts).where(hosts.c.id == id)
        conn.execute(stmt)
        conn.commit()

def list_hosts():
    with engine.connect() as conn:
        stmt = select(hosts)
        result = conn.execute(stmt).fetchall()
        return [dict(row) for row in result]
