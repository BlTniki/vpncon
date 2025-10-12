# from flask import Flask
import logging

from vpncon.config import Config, setup_logging

setup_logging()
logger = logging.getLogger(__name__)
logger.info("Logging is set up")


from vpncon.db import validate_connection

logger.debug("Initializing the DB module")
validate_connection()
logger.debug("Connection validated")
logger.info("DB module is initialized")


# from vpncon.db import db_executor

# r.info("Starting app1...")

# db_executor.open()
# r.info("Starting app2...")
# db_executor.execute("SELECT 1 as one, 2 as two")
# r.info("Starting app3...")
# db_executor.close()
# r.info("Starting app4...")


# app = Flask(__name__)


# if __name__ == "__main__":
    # app.run(debug=True)
