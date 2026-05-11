from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from datetime import date
from app import db
from app.models import Student
from app.utils import add_business_days

manage_student_bp = Blueprint('manage-students', __name__)


@manage_student_bp.route('/manage-students', methods=['GET', 'POST'])
@login_required
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
            try:
                days = int(request.form['custom_window_days'])
                if days < 1:
                    return "Window must be at least 1 business day.", 400
                student.custom_window_days = days
                if student.is_authorized:
                    student.authorization_deadline = add_business_days(date.today(), days)
            except (ValueError, KeyError):
                return "Invalid window value.", 400

        db.session.commit()
        # Preserve search/page state after POST
        q = request.form.get('q', '')
        page = request.form.get('page', 1)
        return redirect(url_for('manage-students.manage_students', q=q, page=page))

    page = request.args.get('page', 1, type=int)
    per_page = 25
    search = request.args.get('q', '').strip()

    query = Student.query
    if search:
        query = query.filter(
            db.or_(
                Student.name.ilike(f'%{search}%'),
                Student.student_id.cast(db.String).ilike(f'%{search}%'),
            )
        )

    pagination = query.order_by(Student.name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('manage_students.html',
                           students=pagination.items,
                           pagination=pagination,
                           search=search)
