import pytest
from vpncon.db.postgres_db import PostgresExecutor

class DummyConn:
    def __init__(self):
        self.closed = False
        self.committed = False
        self.rolled_back = False
    def cursor(self):
        return DummyCursor()
    def commit(self):
        self.committed = True
    def rollback(self):
        self.rolled_back = True
    def close(self):
        self.closed = True

class DummyCursor:
    def __init__(self):
        self.closed = False
        self.description = ('desc',)
        self.query = None
        self.kwargs = None
    def execute(self, query, kwargs):
        self.query = query
        self.kwargs = kwargs
    def fetchall(self):
        return [(1,)]
    def close(self):
        self.closed = True

class DummyPool:
    def __init__(self):
        self.putconn_called = False
        self.last_conn = None
    def getconn(self):
        return DummyConn()
    def putconn(self, conn):
        self.putconn_called = True
        self.last_conn = conn
        conn.closed = True

@pytest.fixture
def pool():
    return DummyPool()

@pytest.fixture
def executor(pool):
    return PostgresExecutor(pool)

def test_open_and_close(executor, pool):
    executor.open()
    assert executor.conn is not None
    assert executor.cur is not None
    conn = executor.conn
    executor.close()
    assert conn.closed is True
    assert pool.putconn_called is True
    assert pool.last_conn is conn
    assert executor.conn is None
    assert executor.cur is None

def test_commit_and_close(executor, pool):
    executor.open()
    conn = executor.conn
    executor.commit_and_close()
    assert conn.committed is True
    assert conn.closed is True
    assert pool.putconn_called is True
    assert pool.last_conn is conn
    assert executor.conn is None
    assert executor.cur is None

def test_rollback_and_close(executor, pool):
    executor.open()
    conn = executor.conn
    executor.rollback_and_close()
    assert conn.rolled_back is True
    assert conn.closed is True
    assert pool.putconn_called is True
    assert pool.last_conn is conn
    assert executor.conn is None
    assert executor.cur is None

def test_execute_returns_data(executor):
    executor.open()
    result = executor.execute("SELECT 1")
    assert result == [(1,)]
    executor.close()

def test_execute_without_open_raises(executor):
    with pytest.raises(RuntimeError):
        executor.execute("SELECT 1")

def test_open_twice_raises(executor):
    executor.open()
    with pytest.raises(RuntimeError):
        executor.open()
    executor.close()
