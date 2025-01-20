from flask import Blueprint, render_template, request, redirect, url_for
from flask_mail import Message
from config import mail
from . import db
from dotenv import load_dotenv
import os
from app.models import Student, Retake, Instructor, Class, RetakeSchedule

schedule_bp = Blueprint('schedule', __name__)
@schedule_bp.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        student_id = request.form['student_id']
        schedule_id = request.form['schedule_id']

        # Check if student exists and is authorized
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return "Student not found.", 404
        if not student.is_authorized:
            return "You are not authorized for a retake.", 403

        # Check if the selected schedule is valid
        selected_slot = RetakeSchedule.query.get(schedule_id)
        if not selected_slot:
            return "Invalid schedule slot.", 400

        # Check capacity
        if selected_slot.current_bookings >= selected_slot.max_capacity:
            return "This time slot is fully booked.", 400

        # Schedule the retake
        new_retake = Retake(student_id=student_id, date=selected_slot.date, time=selected_slot.time)
        db.session.add(new_retake)

        # Update the slot's current bookings
        selected_slot.current_bookings += 1
        db.session.commit()

        # Send email to the instructor
        # instructor_email = student.assigned_class.instructor.email
        # msg = Message(
        #     subject="Student Scheduled a Retake",
        #     sender=os.getenv('MAIL_USERNAME'), 
        #     recipients=[instructor_email],
        #     body=f"Student {student.name} ({student.student_id}) has scheduled a retake on {selected_slot.date} at {selected_slot.time}."
        # )
        # mail.send(msg)

        return "Retake scheduled successfully!"

    # Fetch available slots
    available_slots = RetakeSchedule.query.filter(
        RetakeSchedule.current_bookings < RetakeSchedule.max_capacity
    ).all()
    return render_template('schedule.html', available_slots=available_slots)

