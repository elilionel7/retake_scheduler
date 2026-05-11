from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import login_required
from app import db
from app.generate_schedule import generate_schedule
from app.models import RetakeSchedule, Retake, Class

populate_schedule_bp = Blueprint('populate-schedule', __name__)


@populate_schedule_bp.route('/populate-schedule', methods=['GET'])
@login_required
def populate_schedule_confirm():
    classes = Class.query.order_by(Class.course_name, Class.section).all()
    booked_count = Retake.query.filter_by(status='scheduled').count()
    return render_template('populate_schedule_confirm.html',
                           classes=classes,
                           booked_count=booked_count)


@populate_schedule_bp.route('/populate-schedule', methods=['POST'])
@login_required
def populate_schedule():
    class_id_raw = request.form.get('class_id', '').strip()
    class_id = int(class_id_raw) if class_id_raw else None

    # Only delete slots for the selected class (or all global slots if none selected)
    if class_id:
        RetakeSchedule.query.filter_by(class_id=class_id).delete()
    else:
        RetakeSchedule.query.filter_by(class_id=None).delete()

    schedule = generate_schedule()
    for slot in schedule:
        db.session.add(RetakeSchedule(
            date=slot["date"],
            time=slot["time"],
            max_capacity=5,
            current_bookings=0,
            class_id=class_id,
        ))

    db.session.commit()
    return redirect(url_for('slots.slots_page'))
