# app/__init__.py

from flask import Flask
from .extensions import db, migrate
from config.settings import DevelopmentConfig, ProductionConfig
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints, etc.
    from .routes import register_blueprints
    register_blueprints(app)

    return app
