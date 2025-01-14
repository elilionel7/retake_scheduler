from . import db

class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    # Relationship to Class
    classes = db.relationship('Class', backref='instructor', lazy=True)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)  # e.g., MAT 101
    section = db.Column(db.String(10), nullable=False)       # e.g., Section A
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)

    # Relationship to Students
    students = db.relationship('Student', backref='class', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(10), unique=True, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)

class Retake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(10), db.ForeignKey('student.student_id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
