from flask import Blueprint, render_template, request, redirect, url_for
from app import db  
from app.models import Student

manage_student_bp = Blueprint('manage-students', __name__)
@manage_student_bp.route('/manage-students', methods=['GET', 'POST'])
def manage_students():
    if request.method == 'POST':
        student_id = request.form['student_id']
        action = request.form['action']

        # Find the student
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return "Student not found.", 404

        # Update authorization status
        if action == 'authorize':
            student.is_authorized = True
        elif action == 'deauthorize':
            student.is_authorized = False
        db.session.commit()

        return redirect(url_for('manage-students.manage_students'))

    # Fetch all students
    students = Student.query.all()
    return render_template('manage_students.html', students=students)
