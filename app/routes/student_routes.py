from flask import Blueprint, render_template, request, redirect, url_for
from flask_mail import Message
from config import mail
from . import db
from dotenv import load_dotenv
import os
from app.models import Student

student_bp = Blueprint('student', __name__)
@student_bp.route('/manage_students', methods=['GET', 'POST'])
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

        return redirect(url_for('manage_students'))

    # Fetch all students
    students = Student.query.all()
    return render_template('manage_students.html', students=students)
