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


from flask import Flask
# from vpncon.users import users_bp
app = Flask(__name__)
# app.register_blueprint(users_bp)

api_doc(app, config_path='openapi.yml', url_prefix='/api/doc', title='API doc')




if __name__ == "__main__":
    app.run(debug=True)
