# from flask import Flask
import yaml
import logging
import logging.config

with open('logging.yml', 'r', encoding='utf-8') as f:
    logging_config = yaml.load(f, Loader=yaml.SafeLoader)
logging.config.dictConfig(logging_config)


from vpncon.config import Config

# root_handler = logging.StreamHandler()
# root_handler.setLevel(logging.INFO)
# logging.basicConfig(
#     level=logging.DEBUG,format=Config.LOGGER_FORMAT, handlers=[root_handler],
#     propa
# )

r = logging.getLogger(__name__)
v = logging.getLogger('vpncon')
a = logging.getLogger('vpncon.a')

r.debug("Starting app...")
a.debug("Starting app A...")

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
