from . import db
from datetime import date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Instructor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    classes = db.relationship("Class", backref="instructor", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, unique=True, index=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    is_authorized = db.Column(db.Boolean, default=False)
    attempts_used = db.Column(db.Integer, default=0)
    authorization_deadline = db.Column(db.Date, nullable=True)
    custom_window_days = db.Column(db.Integer, nullable=True)
    assigned_class = db.relationship('Class', back_populates='students')

    @property
    def deadline_passed(self):
        if self.authorization_deadline is None:
            return False
        return date.today() > self.authorization_deadline

    @property
    def effective_window_days(self):
        if self.custom_window_days is not None:
            return self.custom_window_days
        return self.assigned_class.window_days

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey("instructor.id"), nullable=False)
    window_days = db.Column(db.Integer, default=5)
    students = db.relationship("Student", back_populates="assigned_class")

class RetakeSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False, index=True)
    time = db.Column(db.String(5), nullable=False)
    max_capacity = db.Column(db.Integer, default=5)
    current_bookings = db.Column(db.Integer, default=0)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True, index=True)
    assigned_class = db.relationship('Class', backref='retake_slots')

class Retake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False, index=True)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    # status: scheduled | attended | no_show | cancelled
    status = db.Column(db.String(20), default='scheduled', index=True)
    can_modify = db.Column(db.Boolean, default=True, nullable=False)
    reminder_sent = db.Column(db.Boolean, default=False)
    student = db.relationship('Student', backref='retakes')
