from flask import Blueprint, jsonify, request, render_template
from app import db
from app.models import RetakeSchedule
from datetime import date

slot_bp = Blueprint("slots", __name__)


@slot_bp.route("/slots")
def slots_page():
    slots = (
        RetakeSchedule.query
        .order_by(RetakeSchedule.date, RetakeSchedule.time)
        .all()
    )
    today = date.today().strftime('%Y-%m-%d')
    return render_template("slots.html", slots=slots, today=today)


@slot_bp.route("/slots/<int:slot_id>/capacity", methods=["PATCH"])
def update_capacity(slot_id):
    """Instructor updates the max capacity of a slot."""
    if not request.is_json:
        return jsonify({"error": "Expected JSON data"}), 400

    data = request.get_json()
    new_capacity = data.get("max_capacity")

    if new_capacity is None:
        return jsonify({"error": "Missing max_capacity"}), 400

    try:
        new_capacity = int(new_capacity)
    except (ValueError, TypeError):
        return jsonify({"error": "max_capacity must be an integer"}), 400

    slot = RetakeSchedule.query.get(slot_id)
    if not slot:
        return jsonify({"error": "Slot not found"}), 404

    if new_capacity < slot.current_bookings:
        return jsonify({
            "error": f"Cannot set capacity below current bookings ({slot.current_bookings})"
        }), 400

    slot.max_capacity = new_capacity
    db.session.commit()

    return jsonify({
        "message": "Capacity updated.",
        "slot_id": slot_id,
        "max_capacity": slot.max_capacity,
        "current_bookings": slot.current_bookings,
    }), 200
