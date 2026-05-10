from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.models import Instructor

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        instructor = Instructor.query.filter(
            Instructor.email.ilike(email)
        ).first()
        if instructor and instructor.check_password(password):
            login_user(instructor, remember=True)
            next_page = request.args.get('next') or url_for('home-bp.dashboard')
            return redirect(next_page)
        return render_template('login.html', error='Invalid email or password.')
    return render_template('login.html', error=None)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
