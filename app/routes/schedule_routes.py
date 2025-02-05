# app/routes/schedule_routes.py
from flask import Blueprint, render_template, request, jsonify

from flask_mail import Message
from config import mail
from app import db
from dotenv import load_dotenv
import os
from app.models import Student, Retake, RetakeSchedule

schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.route("/schedule", methods=["GET", "POST"])
def schedule():
    if request.method == "POST":
        student_id = request.form["student_id"]
        schedule_id = request.form["schedule_id"]

        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return "Student not found.", 404
        if not student.is_authorized:
            return "You are not authorized for a retake.", 403

        existing_retake = Retake.query.filter_by(student_id=student_id).first()
        if existing_retake:
            return "You already have a scheduled retake.", 400

        selected_slot = RetakeSchedule.query.get(schedule_id)
        if not selected_slot:
            return "Invalid schedule slot.", 400

        if selected_slot.current_bookings >= selected_slot.max_capacity:
            return "This time slot is fully booked.", 400

        new_retake = Retake(
            student_id=student_id, date=selected_slot.date, time=selected_slot.time
        )
        db.session.add(new_retake)

        selected_slot.current_bookings += 1
        db.session.commit()

        return "Retake scheduled successfully!"

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    available_slots_pagination = RetakeSchedule.query.filter(
        RetakeSchedule.current_bookings < RetakeSchedule.max_capacity
    ).paginate(page=page, per_page=per_page, error_out=False)

    available_slots = available_slots_pagination.items

    return render_template(
        "schedule.html",
        available_slots=available_slots,
        pagination=available_slots_pagination,
    )


@schedule_bp.route("/schedule/modify", methods=["PATCH"])
def modify_retake():
    """Modify a student's existing retake schedule (one-time only)."""
    if not request.is_json:
        return jsonify({"error": "Expected JSON data"}), 400

    data = request.get_json()
    student_id = data.get("student_id")
    new_schedule_id = data.get("new_schedule_id")

    if not student_id or not new_schedule_id:
        return jsonify({"error": "Missing student_id or new_schedule_id"}), 400

    existing_retake = Retake.query.filter_by(
        student_id=student_id, status="Scheduled"
    ).first()

    if not existing_retake:
        return (
            jsonify({"error": "No active scheduled retake found for this student."}),
            404,
        )

    if not getattr(existing_retake, "can_modify", True):
        return jsonify({"error": "You have already modified your retake once."}), 400

    new_slot = RetakeSchedule.query.get(new_schedule_id)
    if not new_slot:
        return jsonify({"error": "Invalid schedule slot"}), 400

    if new_slot.current_bookings >= new_slot.max_capacity:
        return jsonify({"error": "New schedule slot is fully booked"}), 400

    old_slot = RetakeSchedule.query.filter_by(
        date=existing_retake.date, time=existing_retake.time
    ).first()

    try:
        if old_slot:
            old_slot.current_bookings -= 1

        new_slot.current_bookings += 1

        existing_retake.date = new_slot.date
        existing_retake.time = new_slot.time
        existing_retake.can_modify = False

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Retake schedule updated successfully.",
                    "new_date": new_slot.date,
                    "new_time": new_slot.time,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database update failed: {str(e)}"}), 500


@schedule_bp.route("/schedule/summary")
def schedule_summary():
    student_id = request.args.get("student_id")
    if not student_id:
        return "No student_id provided.", 400

    retake = Retake.query.filter_by(student_id=student_id, status="Scheduled").first()

    if not retake:
        return f"No scheduled retake found for student {student_id}.", 404

    return render_template("schedule_summary.html", retake=retake)
