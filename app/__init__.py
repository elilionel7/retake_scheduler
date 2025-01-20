from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import configure_app

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    configure_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes
    from app.routes import setup_routes
    setup_routes(app)

    return app
