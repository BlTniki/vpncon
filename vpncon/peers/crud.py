from .model import peers
from sqlalchemy.sql import select, insert, update, delete
from ..db import engine

def get_peer(user_id, host_id):
    with engine.connect() as conn:
        stmt = select(peers).where((peers.c.user_id == user_id) & (peers.c.host_id == host_id))
        result = conn.execute(stmt).fetchone()
        return dict(result) if result else None

def create_peer(user_id, host_id, conf_name, peer_ip, is_activated):
    with engine.connect() as conn:
        stmt = insert(peers).values(user_id=user_id, host_id=host_id, conf_name=conf_name, peer_ip=peer_ip, is_activated=is_activated)
        conn.execute(stmt)
        conn.commit()

def update_peer(user_id, host_id, **fields):
    with engine.connect() as conn:
        stmt = update(peers).where((peers.c.user_id == user_id) & (peers.c.host_id == host_id)).values(**fields)
        conn.execute(stmt)
        conn.commit()

def delete_peer(user_id, host_id):
    with engine.connect() as conn:
        stmt = delete(peers).where((peers.c.user_id == user_id) & (peers.c.host_id == host_id))
        conn.execute(stmt)
        conn.commit()

def list_peers():
    with engine.connect() as conn:
        stmt = select(peers)
        result = conn.execute(stmt).fetchall()
        return [dict(row) for row in result]
