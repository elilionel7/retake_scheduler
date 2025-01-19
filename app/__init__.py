from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import configure_app

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Load configurations
    configure_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register routes
    from app.routes import setup_routes
    setup_routes(app)

    return app
