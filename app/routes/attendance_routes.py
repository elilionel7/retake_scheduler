from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
from app import db
from app.models import Retake, Student
from app.email_utils import send_ineligible_notice

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/sessions")
@login_required
def sessions():
    from datetime import date, timedelta
    today = date.today().strftime('%Y-%m-%d')
    cutoff = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')

    date_filter = request.args.get('date', '').strip()

    upcoming_query = Retake.query.filter_by(status="scheduled").order_by(Retake.date, Retake.time)
    if date_filter:
        upcoming_query = upcoming_query.filter(Retake.date == date_filter)

    upcoming = upcoming_query.all()

    past = (
        Retake.query
        .filter(Retake.status.in_(["attended", "no_show"]))
        .filter(Retake.date >= cutoff)
        .order_by(Retake.date.desc(), Retake.time.desc())
        .all()
    )

    # Distinct upcoming dates for the filter chips
    all_upcoming_dates = (
        db.session.query(Retake.date)
        .filter_by(status="scheduled")
        .distinct()
        .order_by(Retake.date)
        .all()
    )
    upcoming_dates = [r.date for r in all_upcoming_dates]

    return render_template("sessions.html",
                           upcoming=upcoming,
                           past=past,
                           today=today,
                           date_filter=date_filter,
                           upcoming_dates=upcoming_dates)


@attendance_bp.route("/attendance", methods=["POST"])
@login_required
def mark_attendance():
    if not request.is_json:
        return jsonify({"error": "Expected JSON data"}), 400

    data = request.get_json()
    retake_id = data.get("retake_id")
    status = data.get("status")

    if not retake_id or status not in ("attended", "no_show"):
        return jsonify({"error": "Provide retake_id and status (attended or no_show)"}), 400

    retake = Retake.query.get(retake_id)
    if not retake:
        return jsonify({"error": "Retake not found"}), 404

    if retake.status != "scheduled":
        return jsonify({"error": f"Retake is already marked as '{retake.status}'"}), 400

    retake.status = status

    if status == "no_show":
        student = retake.student
        student.attempts_used += 1

        if student.attempts_used >= 2:
            student.is_authorized = False
            db.session.commit()
            try:
                send_ineligible_notice(student)
            except Exception:
                pass
            return jsonify({
                "message": "Marked as no-show. Student has used all attempts and is no longer eligible.",
                "student_id": student.student_id,
                "attempts_used": student.attempts_used,
            }), 200

        db.session.commit()
        return jsonify({
            "message": "Marked as no-show. Student has one attempt remaining.",
            "student_id": student.student_id,
            "attempts_used": student.attempts_used,
        }), 200

    db.session.commit()
    return jsonify({"message": "Marked as attended."}), 200
