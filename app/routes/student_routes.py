from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app import db
from app.models import Student, Class

student_bp = Blueprint("student", __name__)

@student_bp.route("/add-student", methods=["GET", "POST"])
@login_required
def add_student():
    def render_form(error=None, page=1, per_page=10):
        classes_pagination = Class.query.paginate(page=page, per_page=per_page, error_out=False)
        return render_template("add_student.html",
                               classes=classes_pagination.items,
                               pagination=classes_pagination,
                               error=error)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        student_id = request.form.get("student_id", "").strip()
        class_id = request.form.get("class_id", "").strip()

        if not name or not student_id or not class_id:
            return render_form(error="All fields are required.")

        if Student.query.filter_by(student_id=student_id).first():
            return render_form(error=f"Student ID {student_id} is already registered.")

        if not Class.query.get(class_id):
            return render_form(error="Selected class does not exist.")

        new_student = Student(name=name, student_id=student_id, class_id=class_id)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for("home-bp.dashboard"))

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    return render_form(page=page, per_page=per_page)
