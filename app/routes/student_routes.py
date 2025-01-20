from flask import Blueprint, render_template, request, redirect, url_for
from app import db  
from app.models import Student, Class

student_bp = Blueprint('student', __name__)

@student_bp.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        student_id = request.form['student_id']
        class_id = request.form['class_id']
        new_student = Student(name=name, student_id=student_id, class_id=class_id)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('home.home'))

    classes = db.session.query(Class).all()
    return render_template('add_student.html', classes=classes)
