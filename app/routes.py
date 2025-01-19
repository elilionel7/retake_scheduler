from flask import render_template, request, redirect, url_for
from flask_mail import Message
from config import mail
from . import db
from dotenv import load_dotenv
import os
from .models import Student, Retake, Instructor, Class, RetakeSchedule

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
            # Check if the email already exists
            existing_instructor = Instructor.query.filter_by(email=email).first()
            if existing_instructor:
                return render_template('add_instructor.html', error=f"Instructor with email {email} already exists.")

            new_instructor = Instructor(name=name, email=email)
            db.session.add(new_instructor)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('add_instructor.html',  error=None)

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
        
        # Fetch all classes for the dropdown
        classes = Class.query.all()
        return render_template('add_student.html', classes=classes)


    # Route to schedule a retake


    @app.route('/schedule', methods=['GET', 'POST'])
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


    @app.route('/manage_students', methods=['GET', 'POST'])
    def manage_students():
        if request.method == 'POST':
            student_id = request.form['student_id']
            action = request.form['action']

            # Find the student
            student = Student.query.filter_by(id=student_id).first()
            if not student:
                return "Student not found.", 404

            # Update authorization status
            if action == 'authorize':
                student.is_authorized = True
            elif action == 'deauthorize':
                student.is_authorized = False
            db.session.commit()

            return redirect(url_for('manage_students'))

        # Fetch all students
        students = Student.query.all()
        return render_template('manage_students.html', students=students)
