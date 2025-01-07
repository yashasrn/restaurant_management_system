from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from routes import register_routes
from models import db
from extensions import blacklist
from config import Config

# Initialize the Flask app
app = Flask(__name__)

# Load configurations
app.config.from_object(Config)

# Initialize JWT
jwt = JWTManager(app)

# JWT blacklist configuration
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklist

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Register routes
register_routes(app)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.getenv('FLASK_PORT', 8080))
    app.run(host='0.0.0.0', port=port)