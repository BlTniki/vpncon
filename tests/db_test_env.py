
TEST_SCHEMA = "vpncon_test"
CREATE_TEST_DB_SQL = f"CREATE DATABASE {TEST_SCHEMA};"


def setup_test_db():
    """Set up a test database environment."""
    from vpncon.db.db_migrations import DbMigrator, PostgresMigrationExecutor

    # Create test database
    PostgresMigrationExecutor.execute([CREATE_TEST_DB_SQL])

    # Change DB_URI to connect to the test database
    from vpncon.config import Config
    original_db_uri = Config.DB_URI
    Config.DB_URI = original_db_uri.rsplit("/", 1)[0] + f"/{TEST_SCHEMA}"

    # Apply migrations to the test database
    from vpncon.db import validate_connection

    logger.debug("Initializing the DB module")
    validate_connection()
    logger.debug("Connection validated")