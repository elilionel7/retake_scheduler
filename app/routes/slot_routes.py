from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.models import RetakeSchedule, Class
from datetime import date
from collections import OrderedDict

slot_bp = Blueprint("slots", __name__)


def _build_grouped(slots):
    grouped = OrderedDict()
    for slot in slots:
        key = slot.class_id
        if key not in grouped:
            grouped[key] = {
                'label': f"{slot.assigned_class.course_name} · Section {slot.assigned_class.section}" if slot.assigned_class else "Global Slots",
                'instructor': slot.assigned_class.instructor.name if slot.assigned_class else "",
                'by_date': OrderedDict(),
            }
        if slot.date not in grouped[key]['by_date']:
            grouped[key]['by_date'][slot.date] = []
        grouped[key]['by_date'][slot.date].append(slot)
    return grouped


@slot_bp.route("/slots")
@login_required
def slots_page():
    class_id = request.args.get('class_id', type=int)

    query = RetakeSchedule.query.order_by(RetakeSchedule.class_id, RetakeSchedule.date, RetakeSchedule.time)
    if class_id:
        query = query.filter_by(class_id=class_id)

    slots = query.all()
    classes = Class.query.order_by(Class.course_name, Class.section).all()
    today = date.today().strftime('%Y-%m-%d')

    return render_template("slots.html",
                           grouped=_build_grouped(slots),
                           today=today,
                           classes=classes,
                           active_class_id=class_id)


@slot_bp.route("/slots/add", methods=["GET", "POST"])
@login_required
def add_slot():
    classes = Class.query.order_by(Class.course_name, Class.section).all()

    def render_form(error=None):
        return render_template("add_slot.html", classes=classes, error=error)

    if request.method == "POST":
        class_id_raw = request.form.get("class_id", "").strip()
        slot_date   = request.form.get("date", "").strip()
        slot_time   = request.form.get("time", "").strip()
        capacity_raw = request.form.get("max_capacity", "5").strip()

        if not class_id_raw or not slot_date or not slot_time:
            return render_form(error="Class, date, and time are all required.")

        try:
            class_id = int(class_id_raw)
            capacity = max(1, int(capacity_raw))
        except ValueError:
            return render_form(error="Invalid capacity value.")

        if not Class.query.get(class_id):
            return render_form(error="Selected class does not exist.")

        # Prevent duplicate slot for the same class/date/time
        duplicate = RetakeSchedule.query.filter_by(
            class_id=class_id, date=slot_date, time=slot_time
        ).first()
        if duplicate:
            return render_form(error=f"A slot for that class already exists on {slot_date} at {slot_time}.")

        db.session.add(RetakeSchedule(
            class_id=class_id,
            date=slot_date,
            time=slot_time,
            max_capacity=capacity,
            current_bookings=0,
        ))
        db.session.commit()
        return redirect(url_for("slots.slots_page", class_id=class_id))

    return render_form()


@slot_bp.route("/slots/<int:slot_id>/capacity", methods=["PATCH"])
@login_required
def update_capacity(slot_id):
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


@slot_bp.route("/slots/<int:slot_id>/delete", methods=["POST"])
@login_required
def delete_slot(slot_id):
    slot = RetakeSchedule.query.get(slot_id)
    if not slot:
        return jsonify({"error": "Slot not found"}), 404
    if slot.current_bookings > 0:
        return jsonify({"error": f"Cannot delete a slot with {slot.current_bookings} active booking(s)."}), 400

    class_id = slot.class_id
    db.session.delete(slot)
    db.session.commit()
    return jsonify({"message": "Slot deleted."}), 200
