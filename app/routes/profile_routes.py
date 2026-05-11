from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import db

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    error = None
    success = None

    if request.method == 'POST':
        current_pw = request.form.get('current_password', '')
        new_pw = request.form.get('new_password', '').strip()
        confirm_pw = request.form.get('confirm_password', '').strip()

        if not current_user.check_password(current_pw):
            error = "Current password is incorrect."
        elif len(new_pw) < 8:
            error = "New password must be at least 8 characters."
        elif new_pw != confirm_pw:
            error = "New passwords do not match."
        else:
            current_user.set_password(new_pw)
            db.session.commit()
            success = "Password updated successfully."

    return render_template('profile.html', error=error, success=success)
