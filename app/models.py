from . import db
class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    classes = db.relationship("Class", backref="instructor", lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    student_id = db.Column(db.Integer, unique=True, index=True, nullable=False)  
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    is_authorized = db.Column(db.Boolean, default=False)
    assigned_class = db.relationship('Class', back_populates='students')

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey("instructor.id"), nullable=False)
    students = db.relationship("Student", back_populates="assigned_class")

class RetakeSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False, index=True)
    time = db.Column(db.String(5), nullable=False)
    max_capacity = db.Column(db.Integer, default=5)
    current_bookings = db.Column(db.Integer, default=0)

class Retake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False, index=True)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    status = db.Column(db.String(20), default='Scheduled', index=True)
    can_modify = db.Column(db.Boolean, default=True, nullable=False)
    student = db.relationship('Student', backref='retakes')

