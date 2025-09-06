# from flask import Flask
import logging

from vpncon.config import Config

root_handler = logging.StreamHandler()
root_handler.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.DEBUG,format=Config.LOGGER_FORMAT, handlers=[root_handler]
)

r = logging.getLogger(__name__)
a = logging.getLogger('vpncon.a')

r.info("Starting app...")
a.info("Starting app A...")

# app = Flask(__name__)


# if __name__ == "__main__":
    # app.run(debug=True)
