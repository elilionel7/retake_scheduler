

from flask import Blueprint, render_template, request, redirect, url_for
from flask_mail import Message
from config import mail
from . import db
from dotenv import load_dotenv
import os
from app.generate_schedule import generate_schedule
from app.models import  RetakeSchedule

populate_schedule_bp = Blueprint('populate_schedule', __name__)
@populate_schedule_bp.route('/populate_schedule', methods=['GET'])
def populate_schedule():
    # Generate the dynamic schedule
    schedule = generate_schedule()

    # Clear existing schedule (optional)
    RetakeSchedule.query.delete()

    # Add the generated slots to the database
    for slot in schedule:
        new_slot = RetakeSchedule(
            date=slot["date"],
            time=slot["time"],
            max_capacity=5,  # Default capacity
            current_bookings=0  # Initially no bookings
        )
        db.session.add(new_slot)

    db.session.commit()

    return "Schedule populated successfully!"

