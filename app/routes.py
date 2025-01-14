from flask import render_template, request, redirect, url_for
from . import db
from .models import Student, Retake, Instructor, Class

def setup_routes(app):

    # Home route
    @app.route('/')
    def home():
        return "Welcome to the Retake Scheduler App!"

    # Route to add an instructor
    @app.route('/add_instructor', methods=['GET', 'POST'])
    def add_instructor():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            new_instructor = Instructor(name=name, email=email)
            db.session.add(new_instructor)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('add_instructor.html')

    # Route to add a class
    @app.route('/add_class', methods=['GET', 'POST'])
    def add_class():
        if request.method == 'POST':
            course_name = request.form['course_name']
            section = request.form['section']
            instructor_id = request.form['instructor_id']
            new_class = Class(course_name=course_name, section=section, instructor_id=instructor_id)
            db.session.add(new_class)
            db.session.commit()
            return redirect(url_for('home'))
        instructors = Instructor.query.all()
        return render_template('add_class.html', instructors=instructors)

    # Route to add a student
    @app.route('/add_student', methods=['GET', 'POST'])
    def add_student():
        if request.method == 'POST':
            name = request.form['name']
            student_id = request.form['student_id']
            class_id = request.form['class_id']
            new_student = Student(name=name, student_id=student_id, class_id=class_id)
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for('home'))
        classes = Class.query.all()
        return render_template('add_student.html', classes=classes)

    # Route to schedule a retake
    @app.route('/schedule', methods=['GET', 'POST'])
    def schedule():
        if request.method == 'POST':
            student_id = request.form['student_id']
            retake_date = request.form['date']
            new_retake = Retake(student_id=student_id, date=retake_date)
            db.session.add(new_retake)
            db.session.commit()
            return redirect(url_for('home'))
        students = Student.query.all()
        return render_template('schedule.html', students=students)
