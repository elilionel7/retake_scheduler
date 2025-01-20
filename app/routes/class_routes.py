from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Class, Instructor

class_bp = Blueprint('class', __name__)

@class_bp.route('/add_class', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        course_name = request.form['course_name']
        section = request.form['section']
        instructor_id = request.form['instructor_id']
        new_class = Class(course_name=course_name, section=section, instructor_id=instructor_id)
        db.session.add(new_class)
        db.session.commit()
        return redirect(url_for('home.home'))
    instructors = Instructor.query.all()
    return render_template('add_class.html', instructors=instructors)
