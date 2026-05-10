from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app import db
from app.models import Instructor

instructor_bp = Blueprint('instructor', __name__)

@instructor_bp.route('/add-instructor', methods=['GET', 'POST'])
@login_required
def add_instructor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()

        if not password:
            return render_template('add_instructor.html', error="Password is required.")
        if password != confirm:
            return render_template('add_instructor.html', error="Passwords do not match.")

        existing_instructor = Instructor.query.filter_by(email=email).first()
        if existing_instructor:
            return render_template('add_instructor.html', error=f"Instructor with email {email} already exists.")

        new_instructor = Instructor(name=name, email=email)
        new_instructor.set_password(password)
        db.session.add(new_instructor)
        db.session.commit()
        return redirect(url_for('home-bp.dashboard'))

    return render_template('add_instructor.html', error=None)


