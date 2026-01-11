import pytest
from collections import Counter
from vpncon.db import auto_transaction
from vpncon.hosts.service import HostServiceCRUD
from vpncon.hosts.model import Host
from vpncon.exceptions import EntityAlreadyExistsException, EntityNotExistsException
from vpncon.hosts.crud import get_ip_pool_for_host

@pytest.fixture
def service():
    return HostServiceCRUD()

@auto_transaction(always_rollback=True)
def test_create_host_success(service):
    service.create_host(host_id=1, name='test_host', ip_address='192.168.1.1', port=22, host_password='password123')
    host = service.get_host(1)
    assert host is not None
    assert host.id == 1
    assert host.name == 'test_host'
    assert host.ip_address == '192.168.1.1'
    assert host.port == 22
    assert host.host_password == 'password123'
    
    # Check IP pool is created
    ip_pool = get_ip_pool_for_host(1)
    expected_ips = [f"10.8.0.{i}" for i in range(2, 255)]
    assert Counter(ip_pool) == Counter(expected_ips)

@auto_transaction(always_rollback=True)
def test_create_host_conflict(service):
    service.create_host(2, 'host2', '192.168.1.2', 22, 'pass2')
    with pytest.raises(EntityAlreadyExistsException):
        service.create_host(2, 'host2_dup', '192.168.1.3', 23, 'pass3')

@auto_transaction(always_rollback=True)
def test_get_host_not_exists(service):
    assert service.get_host(999999) is None

@auto_transaction(always_rollback=True)
def test_update_host_success(service):
    service.create_host(3, 'host3', '192.168.1.3', 22, 'pass3')

    service.update_host(3, 'updated_host', '192.168.1.4', 23, 'newpass')
    host = service.get_host(3)

    assert host.name == 'updated_host'
    assert host.ip_address == '192.168.1.4'
    assert host.port == 23
    assert host.host_password == 'newpass'

@auto_transaction(always_rollback=True)
def test_update_host_not_exists(service):
    with pytest.raises(EntityNotExistsException):
        service.update_host(500000, 'name', 'ip', 22, 'pass')

@auto_transaction(always_rollback=True)
def test_delete_host_success(service):
    service.create_host(4, 'host4', '192.168.1.4', 22, 'pass4')
    # Verify IP pool exists before deletion
    ip_pool_before = get_ip_pool_for_host(4)
    assert len(ip_pool_before) > 0
    
    service.delete_host(4)
    assert service.get_host(4) is None
    
    # Check IP pool is deleted
    ip_pool_after = get_ip_pool_for_host(4)
    assert ip_pool_after == []

@auto_transaction(always_rollback=True)
def test_delete_host_not_exists(service):
    with pytest.raises(EntityNotExistsException):
        service.delete_host(123456)