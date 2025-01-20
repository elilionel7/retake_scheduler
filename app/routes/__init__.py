from .instructor_routes import instructor_bp
from .student_routes import student_bp
from .class_routes import class_bp
from .schedule_routes import schedule_bp
from .populate_schedule_routes import populate_schedule_bp
from home_routes import home_bp

def setup_routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(instructor_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(class_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(populate_schedule_bp)
