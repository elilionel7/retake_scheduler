from flask import Blueprint, render_template, request, jsonify
from datetime import date
from app import db
from app.models import Student, Retake, RetakeSchedule
from app.email_utils import send_booking_confirmation

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
        if student.attempts_used >= 2:
            return "You have used all of your retake attempts.", 403
        if student.deadline_passed:
            return "Your retake window has expired. Please contact your instructor.", 403

        existing_retake = Retake.query.filter_by(
            student_id=student_id, status="scheduled"
        ).first()
        if existing_retake:
            return "You already have a scheduled retake.", 400

        selected_slot = RetakeSchedule.query.get(schedule_id)
        if not selected_slot:
            return "Invalid schedule slot.", 400
        if selected_slot.current_bookings >= selected_slot.max_capacity:
            return "This time slot is fully booked.", 400

        new_retake = Retake(
            student_id=student_id,
            date=selected_slot.date,
            time=selected_slot.time,
        )
        db.session.add(new_retake)
        selected_slot.current_bookings += 1
        db.session.commit()

        try:
            send_booking_confirmation(student, new_retake)
        except Exception:
            pass

        return "Retake scheduled successfully!"

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    available_slots_pagination = RetakeSchedule.query.filter(
        RetakeSchedule.current_bookings < RetakeSchedule.max_capacity
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "schedule.html",
        available_slots=available_slots_pagination.items,
        pagination=available_slots_pagination,
    )


@schedule_bp.route("/schedule/cancel", methods=["POST"])
def cancel_retake():
    """Voluntary cancellation — no attempt penalty as long as within deadline."""
    data = request.get_json() if request.is_json else request.form
    student_id = data.get("student_id")

    if not student_id:
        return jsonify({"error": "Missing student_id"}), 400

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    if student.deadline_passed:
        return jsonify({"error": "Your retake window has expired."}), 403

    retake = Retake.query.filter_by(student_id=student_id, status="scheduled").first()
    if not retake:
        return jsonify({"error": "No active scheduled retake found."}), 404

    slot = RetakeSchedule.query.filter_by(date=retake.date, time=retake.time).first()
    if slot:
        slot.current_bookings = max(0, slot.current_bookings - 1)

    retake.status = "cancelled"
    retake.reminder_sent = False
    db.session.commit()

    return jsonify({"message": "Retake cancelled. You may rebook before your deadline."}), 200


@schedule_bp.route("/schedule/modify", methods=["PATCH"])
def modify_retake():
    """One-time slot change while still within the authorization window."""
    if not request.is_json:
        return jsonify({"error": "Expected JSON data"}), 400

    data = request.get_json()
    student_id = data.get("student_id")
    new_schedule_id = data.get("new_schedule_id")

    if not student_id or not new_schedule_id:
        return jsonify({"error": "Missing student_id or new_schedule_id"}), 400

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    if student.deadline_passed:
        return jsonify({"error": "Your retake window has expired."}), 403

    existing_retake = Retake.query.filter_by(
        student_id=student_id, status="scheduled"
    ).first()
    if not existing_retake:
        return jsonify({"error": "No active scheduled retake found."}), 404
    if not existing_retake.can_modify:
        return jsonify({"error": "You have already used your one-time modification."}), 400

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
            old_slot.current_bookings = max(0, old_slot.current_bookings - 1)

        new_slot.current_bookings += 1
        existing_retake.date = new_slot.date
        existing_retake.time = new_slot.time
        existing_retake.can_modify = False
        existing_retake.reminder_sent = False
        db.session.commit()

        return jsonify({
            "message": "Retake schedule updated successfully.",
            "new_date": new_slot.date,
            "new_time": new_slot.time,
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database update failed: {str(e)}"}), 500


@schedule_bp.route("/schedule/status")
def schedule_status():
    """Returns the current retake status for a student (JSON)."""
    student_id = request.args.get("student_id")
    if not student_id:
        return jsonify({"error": "Missing student_id"}), 400

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    existing = Retake.query.filter_by(student_id=student_id, status="scheduled").first()
    return jsonify({
        "name": student.name,
        "authorized": student.is_authorized,
        "attempts_used": student.attempts_used,
        "deadline": student.authorization_deadline.isoformat() if student.authorization_deadline else None,
        "deadline_passed": student.deadline_passed,
        "existing_retake": {
            "id": existing.id,
            "date": existing.date,
            "time": existing.time,
            "can_modify": existing.can_modify,
        } if existing else None,
    })


@schedule_bp.route("/schedule/summary")
def schedule_summary():
    student_id = request.args.get("student_id")
    if not student_id:
        return "No student_id provided.", 400

    retake = Retake.query.filter_by(student_id=student_id, status="scheduled").first()
    if not retake:
        return f"No scheduled retake found for student {student_id}.", 404

    return render_template("schedule_summary.html", retake=retake)
