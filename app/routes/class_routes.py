from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app import db
from app.models import Class, Instructor

class_bp = Blueprint('class', __name__)


@class_bp.route('/add-class', methods=['GET', 'POST'])
@login_required
def add_class():
    def render_form(error=None):
        instructors = Instructor.query.order_by(Instructor.name).all()
        return render_template('add_class.html', instructors=instructors, error=error)

    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        section = request.form.get('section', '').strip()
        instructor_id = request.form.get('instructor_id', '').strip()

        if not course_name or not section or not instructor_id:
            return render_form(error="All fields are required.")

        try:
            window_days = int(request.form.get('window_days', 5))
            if window_days < 1:
                window_days = 5
        except ValueError:
            window_days = 5

        if Class.query.filter_by(course_name=course_name, section=section).first():
            return render_form(error=f"{course_name} section {section} already exists.")

        if not Instructor.query.get(instructor_id):
            return render_form(error="Selected instructor does not exist.")

        new_class = Class(
            course_name=course_name,
            section=section,
            instructor_id=instructor_id,
            window_days=window_days,
        )
        db.session.add(new_class)
        db.session.commit()
        return redirect(url_for('home-bp.dashboard'))

    return render_form()
