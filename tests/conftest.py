import pytest
from tests.db_test_env import setup_test_db
from vpncon.config import setup_logging

setup_logging()

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    """Создаёт и уничтожает тестовую базу один раз за сессию pytest."""
    setup_test_db()
    yield