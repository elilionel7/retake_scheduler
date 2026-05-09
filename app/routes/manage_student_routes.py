from flask import Blueprint, render_template, request, redirect, url_for
from datetime import date
from app import db
from app.models import Student
from app.utils import add_business_days

manage_student_bp = Blueprint('manage-students', __name__)


@manage_student_bp.route('/manage-students', methods=['GET', 'POST'])
def manage_students():
    if request.method == 'POST':
        student_id = request.form['student_id']
        action = request.form['action']

        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return "Student not found.", 404

        if action == 'authorize':
            window = student.custom_window_days or student.assigned_class.window_days
            student.is_authorized = True
            student.attempts_used = 0
            student.authorization_deadline = add_business_days(date.today(), window)

        elif action == 'deauthorize':
            student.is_authorized = False
            student.authorization_deadline = None

        elif action == 'set_window':
            # Instructor sets a custom window for this student (special case override)
            try:
                days = int(request.form['custom_window_days'])
                if days < 1:
                    return "Window must be at least 1 business day.", 400
                student.custom_window_days = days
                # If already authorized, recalculate deadline from today using the new window
                if student.is_authorized:
                    student.authorization_deadline = add_business_days(date.today(), days)
            except (ValueError, KeyError):
                return "Invalid window value.", 400

        db.session.commit()
        return redirect(url_for('manage-students.manage_students'))

    students = Student.query.all()
    return render_template('manage_students.html', students=students)
