# from flask import Flask
import logging

from vpncon.config import Config, setup_logging

setup_logging()

logger = logging.getLogger(__name__)
logger.info("Logging is set up")

from vpncon.db import db_executor

# root_handler = logging.StreamHandler()
# root_handler.setLevel(logging.INFO)
# logging.basicConfig(
#     level=logging.DEBUG,format=Config.LOGGER_FORMAT, handlers=[root_handler],
#     propa
# )


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
