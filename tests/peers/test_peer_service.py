import pytest
from decimal import Decimal
from vpncon.db import auto_transaction
from vpncon.peers.service import PeerServiceCRUD
from vpncon.exceptions import (
    EntityAlreadyExistsException,
    EntityNotExistsException,
    EntityValidationFailedException,
)
from vpncon.db import get_db_executor


@pytest.fixture
def service():
    return PeerServiceCRUD()


@auto_transaction(always_rollback=True)
def test_create_peer_success(monkeypatch, service):
    # prepare DB: create user, host and host_ip_pool entries
    db = get_db_executor()
    db.execute("CREATE TABLE IF NOT EXISTS host_ip_pool (host_id BIGINT, peer_ip VARCHAR(255), is_used BOOLEAN)")
    db.execute("INSERT INTO users (telegram_id, telegram_nick, role) VALUES (%(id)s, 't1', 'ACTIVATED_USER') ON CONFLICT DO NOTHING", id=10)
    db.execute("INSERT INTO hosts (id, name, ip_address, port, host_password) VALUES (%(hid)s, 'h1', '1.1.1.1', 1194, 'p') ON CONFLICT DO NOTHING", hid=1)
    # insert one free ip for host
    db.execute("INSERT INTO host_ip_pool (host_id, peer_ip, is_used) VALUES (%(hid)s, %(ip)s, false)", hid=1, ip='10.8.0.2')

    # Mock only HostClient
    call_count = []
    class FakeHC:
        def __init__(self, peer):
            self.peer = peer
        def create_peer_on_host(self):
            call_count.append(1)

    monkeypatch.setattr("vpncon.peers.service.HostClient", FakeHC)

    service.create_peer(telegram_id=10, host_id=1, conf_name="conf1")
    # ensure peer exists via service.get_peer
    p = service.get_peer(10, "conf1")
    assert p is not None
    assert len(call_count) == 1


@auto_transaction(always_rollback=True)
def test_create_peer_conflict(monkeypatch, service):
    # prepare DB and create initial peer
    db = get_db_executor()
    db.execute("INSERT INTO users (telegram_id, telegram_nick, role) VALUES (%(id)s, 't2', 'ACTIVATED_USER') ON CONFLICT DO NOTHING", id=20)
    db.execute("INSERT INTO hosts (id, name, ip_address, port, host_password) VALUES (%(hid)s, 'h2', '1.1.1.2', 1194, 'p') ON CONFLICT DO NOTHING", hid=1)
    db.execute("INSERT INTO host_ip_pool (host_id, peer_ip, is_used) VALUES (%(hid)s, %(ip)s, false)", hid=1, ip='10.8.0.3')
    db.execute("INSERT INTO host_ip_pool (host_id, peer_ip, is_used) VALUES (%(hid)s, %(ip)s, false)", hid=1, ip='10.8.0.4')
    # db.execute("INSERT INTO peers (user_id, host_id, conf_name, peer_ip, is_active) VALUES (%(uid)s, %(hid)s, 'confA', %(ip)s, true)", uid=20, hid=1, ip='10.8.0.3')

    # Mock only HostClient
    call_count = []
    class FakeHC:
        def __init__(self, peer):
            self.peer = peer
        def create_peer_on_host(self):
            call_count.append(1)

    monkeypatch.setattr("vpncon.peers.service.HostClient", FakeHC)


    service.create_peer(20, 1, "confA")
    # second create should raise
    with pytest.raises(EntityAlreadyExistsException):
        service.create_peer(20, 1, "confA")
    assert len(call_count) == 1


@auto_transaction(always_rollback=True)
def test_create_peer_no_ip(monkeypatch, service):
    # ensure no ip entries for host
    db = get_db_executor()
    db.execute("INSERT INTO users (telegram_id, telegram_nick, role) VALUES (%(id)s, 't3', 'ACTIVATED_USER') ON CONFLICT DO NOTHING", id=30)
    db.execute("INSERT INTO hosts (id, name, ip_address, port, host_password) VALUES (%(hid)s, 'h3', '1.1.1.3', 1194, 'p') ON CONFLICT DO NOTHING", hid=99)
    # do not insert host_ip_pool rows for host 99
    with pytest.raises(EntityValidationFailedException):
        service.create_peer(30, 99, "confX")


@auto_transaction(always_rollback=True)
def test_get_peer_not_exists(monkeypatch, service):
    assert service.get_peer(9999, "no") is None


@auto_transaction(always_rollback=True)
def test_switch_peer_active_status_success(monkeypatch, service):
    # prepare DB: create user, host, host_ip_pool and peer
    db = get_db_executor()
    db.execute("INSERT INTO users (telegram_id, telegram_nick, role) VALUES (%(id)s, 't4', 'ACTIVATED_USER') ON CONFLICT DO NOTHING", id=40)
    db.execute("INSERT INTO hosts (id, name, ip_address, port, host_password) VALUES (%(hid)s, 'h4', '1.1.1.4', 1194, 'p') ON CONFLICT DO NOTHING", hid=5)
    db.execute("INSERT INTO host_ip_pool (host_id, peer_ip, is_used) VALUES (%(hid)s, %(ip)s, false)", hid=5, ip='10.8.0.10')
    db.execute("INSERT INTO peers (user_id, host_id, conf_name, peer_ip, is_active) VALUES (%(uid)s, %(hid)s, 'confB', %(ip)s, true)", uid=40, hid=5, ip='10.8.0.10')

    # Mock only HostClient
    activated_calls = []
    deactivated_calls = []
    class FakeHC:
        def __init__(self, peer):
            self.peer = peer
            self.activated = False
            self.deactivated = False
        def activate_on_host(self):
            activated_calls.append(1)
        def deactivate_on_host(self):
            deactivated_calls.append(1)

    monkeypatch.setattr("vpncon.peers.service.HostClient", FakeHC)

    switched = []
    def capture_switch(u, c, is_active):
        switched.append((u, c, is_active))
    # use real switch implementation but patch lower-level crud to capture change
    monkeypatch.setattr("vpncon.peers.service.switch_peer_active_status", lambda u, c, is_active: capture_switch(u, c, is_active))

    service.switch_peer_active_status(40, "confB", True)
    assert switched == [(40, "confB", True)]
    assert len(activated_calls) == 1
    assert len(deactivated_calls) == 0

    service.switch_peer_active_status(40, "confB", False)
    assert switched[-1] == (40, "confB", False)
    assert len(activated_calls) == 1
    assert len(deactivated_calls) == 1


@auto_transaction(always_rollback=True)
def test_delete_peer_success(monkeypatch, service):
    # prepare DB and create peer
    db = get_db_executor()
    db.execute("INSERT INTO users (telegram_id, telegram_nick, role) VALUES (%(id)s, 't5', 'ACTIVATED_USER') ON CONFLICT DO NOTHING", id=50)
    db.execute("INSERT INTO hosts (id, name, ip_address, port, host_password) VALUES (%(hid)s, 'h5', '1.1.1.5', 1194, 'p') ON CONFLICT DO NOTHING", hid=7)
    db.execute("INSERT INTO host_ip_pool (host_id, peer_ip, is_used) VALUES (%(hid)s, %(ip)s, false)", hid=7, ip='10.8.0.20')
    db.execute("INSERT INTO peers (user_id, host_id, conf_name, peer_ip, is_active) VALUES (%(uid)s, %(hid)s, 'confC', %(ip)s, true)", uid=50, hid=7, ip='10.8.0.20')

    call_count = []
    class FakeHC:
        def __init__(self, peer):
            self.peer = peer
        def delete_peer_on_host(self):
            call_count.append(1)
    monkeypatch.setattr("vpncon.peers.service.HostClient", FakeHC)

    # now delete
    service.delete_peer(50, "confC")
    assert service.get_peer(50, "confC") is None
    assert len(call_count) == 1


@auto_transaction(always_rollback=True)
def test_delete_peer_not_exists(monkeypatch, service):
    with pytest.raises(EntityNotExistsException):
        service.delete_peer(60, "nope")


@auto_transaction(always_rollback=True)
def test_deactivate_all_peers(monkeypatch, service):
    # prepare DB and create multiple peers
    db = get_db_executor()
    db.execute("INSERT INTO users (telegram_id, telegram_nick, role) VALUES (%(id)s, 't6', 'ACTIVATED_USER') ON CONFLICT DO NOTHING", id=60)
    db.execute("INSERT INTO hosts (id, name, ip_address, port, host_password) VALUES (%(hid)s, 'h5', '1.1.1.5', 1194, 'p') ON CONFLICT DO NOTHING", hid=7)
    db.execute("INSERT INTO host_ip_pool (host_id, peer_ip, is_used) VALUES (%(hid)s, %(ip)s, false)", hid=7, ip='10.8.0.20')
    db.execute("INSERT INTO peers (user_id, host_id, conf_name, peer_ip, is_active) VALUES (%(uid)s, %(hid)s, 'confD', %(ip)s, true)", uid=60, hid=7, ip='10.8.0.20')
    db.execute("INSERT INTO peers (user_id, host_id, conf_name, peer_ip, is_active) VALUES (%(uid)s, %(hid)s, 'confE', %(ip)s, true)", uid=60, hid=7, ip='10.8.0.21')

    call_count = []
    class FakeHC:
        def __init__(self, peer):
            self.peer = peer
        def deactivate_on_host(self):
            call_count.append(1)
    monkeypatch.setattr("vpncon.peers.service.HostClient", FakeHC)

    # now deactivate all
    service.deactivate_all_peers(60)
    assert service.get_peer(60, "confD") is not None
    assert service.get_peer(60, "confE") is not None
    assert service.get_peer(60, "confD").is_active is False
    assert service.get_peer(60, "confE").is_active is False
    assert len(call_count) == 2

