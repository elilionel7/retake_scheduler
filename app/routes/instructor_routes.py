from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Instructor

instructor_bp = Blueprint('instructor', __name__)

@instructor_bp.route('/add_instructor', methods=['GET', 'POST'])
def add_instructor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        existing_instructor = Instructor.query.filter_by(email=email).first()
        if existing_instructor:
            return render_template('add_instructor.html', error=f"Instructor with email {email} already exists.")

        new_instructor = Instructor(name=name, email=email)
        db.session.add(new_instructor)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_instructor.html', error=None)


