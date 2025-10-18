import logging


logger = logging.getLogger(__name__)


TEST_SCHEMA = "vpncon_test"
DROP_TEST_DB_SQL = f"DROP DATABASE IF EXISTS {TEST_SCHEMA}"
CREATE_TEST_DB_SQL = f"CREATE DATABASE {TEST_SCHEMA};"


def setup_test_db():
    """Set up a test database environment."""
    from vpncon.config import Config

    from vpncon.db.db_migrations import DbMigrator, PostgresMigrationExecutor

    # Create test database
    logger.info("Creating test db")
    PostgresMigrationExecutor.execute([DROP_TEST_DB_SQL], autocommit=True)
    PostgresMigrationExecutor.execute([CREATE_TEST_DB_SQL], autocommit=True)

    # Change DB_URI to connect to the test database
    original_db_uri = Config.DB_URI
    Config.DB_URI = original_db_uri.rsplit("/", 1)[0] + f"/{TEST_SCHEMA}"

    # Apply migrations to the test database
    logger.info("Applying DB migrations")
    DbMigrator(PostgresMigrationExecutor).apply_migrations()


    from vpncon.db import validate_connection

    validate_connection()
    logger.debug("Connection validated")
