from . import db


class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    # Relationship to Class
    classes = db.relationship("Class", backref="instructor", lazy=True)


class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)  # Changed to Integer and Primary Key
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    is_authorized = db.Column(db.Boolean, default=False)

    # Explicit back_populates relationship
    assigned_class = db.relationship('Class', back_populates='students')

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    instructor_id = db.Column(
        db.Integer, db.ForeignKey("instructor.id"), nullable=False
    )

    # Explicit back_populates relationship
    students = db.relationship("Student", back_populates="assigned_class")


class RetakeSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)  # Example: "2025-01-15"
    time = db.Column(db.String(5), nullable=False)  # Example: "14:00"
    max_capacity = db.Column(db.Integer, default=5)  # Max students allowed
    current_bookings = db.Column(db.Integer, default=0)  # Current student count


class Retake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)  # Updated Foreign Key
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Completed, Canceled

    # Optional: Define relationship to Student
    student = db.relationship('Student', backref='retakes')
