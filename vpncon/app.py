from .users.api import bp as users_bp
from .subscriptions.api import bp as subscriptions_bp
from .users_subscriptions.api import bp as users_subscriptions_bp
from .hosts.api import bp as hosts_bp
from .peers.api import bp as peers_bp
from flask import Flask

app = Flask(__name__)

# Register blueprints for all entities
app.register_blueprint(users_bp)
app.register_blueprint(subscriptions_bp)
app.register_blueprint(users_subscriptions_bp)
app.register_blueprint(hosts_bp)
app.register_blueprint(peers_bp)

if __name__ == "__main__":
    app.run(debug=True)
