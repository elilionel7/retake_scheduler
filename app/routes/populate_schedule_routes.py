from flask import Blueprint, redirect, url_for
from flask_login import login_required
from app import db
from app.generate_schedule import generate_schedule
from app.models import RetakeSchedule

populate_schedule_bp = Blueprint('populate-schedule', __name__)


@populate_schedule_bp.route('/populate-schedule', methods=['GET'])
@login_required
def populate_schedule():
    schedule = generate_schedule()

    RetakeSchedule.query.delete()

    for slot in schedule:
        db.session.add(RetakeSchedule(
            date=slot["date"],
            time=slot["time"],
            max_capacity=5,
            current_bookings=0,
        ))

    db.session.commit()
    return redirect(url_for('slots.slots_page'))
