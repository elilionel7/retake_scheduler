from flask import Blueprint, render_template
from flask_login import login_required
from app.extensions import db
from app.models import Student, Retake, RetakeSchedule
from datetime import date

home_bp = Blueprint('home-bp', __name__)

@home_bp.route('/')
def home():
    return render_template('home.html')

@home_bp.route('/dashboard')
@login_required
def dashboard():
    total_students    = Student.query.count()
    authorized_count  = Student.query.filter_by(is_authorized=True).count()
    scheduled_retakes = Retake.query.filter_by(status='scheduled').count()
    available_slots   = RetakeSchedule.query.filter(
        RetakeSchedule.current_bookings < RetakeSchedule.max_capacity,
        RetakeSchedule.date >= date.today().strftime('%Y-%m-%d')
    ).count()
    return render_template('dashboard.html',
        total_students=total_students,
        authorized_count=authorized_count,
        scheduled_retakes=scheduled_retakes,
        available_slots=available_slots,
    )
