from flask import Flask
from .extensions import db, migrate, cache, mail, scheduler, login_manager
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
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access the admin area.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import Instructor
        return Instructor.query.get(int(user_id))

    from .scheduler_jobs import register_jobs
    register_jobs(scheduler)
    scheduler.init_app(app)
    scheduler.start()

    from .routes import register_blueprints
    register_blueprints(app)

    return app
