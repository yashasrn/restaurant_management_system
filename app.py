from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from routes import register_routes
from models import db
from extensions import blacklist

# Initialize the Flask app
app = Flask(__name__)

# Configure the database (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure JWT
app.config['JWT_SECRET_KEY'] = '3d6b5b840e9db2b2fcfe447ad9b6c4b0328e87d04d17a0d6ba9f778e1f01d4cf'
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

# Create tables (only runs once to initialize the database)
with app.app_context():
    db.create_all()

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
