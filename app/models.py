from . import db


class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    # Relationship to Class
    classes = db.relationship("Class", backref="instructor", lazy=True)



class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(10), unique=True, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    is_authorized = db.Column(db.Boolean, default=False)

    # Explicit back_populates relationship
    assigned_class = db.relationship('Class', back_populates='students')

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)

    # Explicit back_populates relationship
    students = db.relationship('Student', back_populates='assigned_class')


class RetakeSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)  # Example: "2025-01-15"
    time = db.Column(db.String(5), nullable=False)   # Example: "14:00"
    max_capacity = db.Column(db.Integer, default=5)  # Max students allowed
    current_bookings = db.Column(db.Integer, default=0)  # Current student count


class Retake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(10), db.ForeignKey('student.student_id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Date of the retake
    time = db.Column(db.String(5), nullable=False)   # Time of the retake


