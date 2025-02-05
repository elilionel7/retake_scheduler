from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Student, Class

student_bp = Blueprint("student", __name__)

@student_bp.route("/add-student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        student_id = request.form["student_id"]
        class_id = request.form["class_id"]

        new_student = Student(name=name, student_id=student_id, class_id=class_id)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for("home-bp.home"))

    
    page = request.args.get("page", 1, type=int)         
    per_page = request.args.get("per_page", 10, type=int) 

    classes_pagination = Class.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    classes = classes_pagination.items

    return render_template(
        "add_student.html",
        classes=classes,
        pagination=classes_pagination
    )
