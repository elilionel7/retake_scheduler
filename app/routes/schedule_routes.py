# app/routes/schedule_routes.py
from flask import Blueprint, render_template, request, jsonify

from flask_mail import Message
from config import mail
from app import db 
from dotenv import load_dotenv
import os
from app.models import Student, Retake, RetakeSchedule

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

        # Check if the student already has an active scheduled retake
        existing_retake = Retake.query.filter_by(student_id=student_id).first()
        if existing_retake:
            return "You already have a scheduled retake.", 400

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



@schedule_bp.route('/retakes/modify', methods=['PATCH'])
def modify_retake():
    """Modify a student's existing retake schedule (one-time only)."""
    if not request.is_json:
        return jsonify({"error": "Expected JSON data"}), 400

    data = request.get_json()
    student_id = data.get('student_id')
    new_schedule_id = data.get('new_schedule_id')

    if not student_id or not new_schedule_id:
        return jsonify({"error": "Missing student_id or new_schedule_id"}), 400

    # 1. Find the student's existing "Scheduled" retake
    existing_retake = Retake.query.filter_by(
        student_id=student_id,
        status='Scheduled'
    ).first()

    if not existing_retake:
        return jsonify({"error": "No active scheduled retake found for this student."}), 404

    # 2. Check if can_modify is still True
    if not getattr(existing_retake, 'can_modify', True):
        return jsonify({"error": "You have already modified your retake once."}), 400

    # 3. Validate the new schedule slot
    new_slot = RetakeSchedule.query.get(new_schedule_id)
    if not new_slot:
        return jsonify({"error": "Invalid schedule slot"}), 400

    if new_slot.current_bookings >= new_slot.max_capacity:
        return jsonify({"error": "New schedule slot is fully booked"}), 400

    # 4. Free the old slot
    old_slot = RetakeSchedule.query.filter_by(
        date=existing_retake.date,
        time=existing_retake.time
    ).first()

    # 5. Attempt the update in a DB transaction
    try:
        if old_slot:
            old_slot.current_bookings -= 1

        new_slot.current_bookings += 1

        existing_retake.date = new_slot.date
        existing_retake.time = new_slot.time
        existing_retake.can_modify = False  # Student used their one chance

        db.session.commit()

        return jsonify({
            "message": "Retake schedule updated successfully.",
            "new_date": new_slot.date,
            "new_time": new_slot.time
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database update failed: {str(e)}"}), 500

