# seed.py

from app import create_app
from app.extensions import db
from app.models import Instructor, Class, Student, RetakeSchedule, Retake
from datetime import datetime, time

def seed_data():
    app = create_app()
    with app.app_context():
        # Optional: Clear existing data to prevent duplicates
        # Uncomment the following lines if you want to reset the data each time
        # db.session.query(Retake).delete()
        # db.session.query(RetakeSchedule).delete()
        # db.session.query(Student).delete()
        # db.session.query(Class).delete()
        # db.session.query(Instructor).delete()

        # Check if data already exists to prevent duplicates
        if Instructor.query.first() or Class.query.first() or Student.query.first() or RetakeSchedule.query.first():
            print("Data already exists. Skipping seeding.")
            return

        # ---------------------------
        # Create Instructors
        # ---------------------------
        instructor1 = Instructor(name="Dr. Alice Smith", email="alice.smith@example.com")
        instructor2 = Instructor(name="Prof. Bob Johnson", email="bob.johnson@example.com")
        instructor3 = Instructor(name="Dr. Carol Williams", email="carol.williams@example.com")

        db.session.add_all([instructor1, instructor2, instructor3])
        db.session.commit()

        # ---------------------------
        # Create Classes
        # ---------------------------
        class1 = Class(course_name="Mat 101", section="H001", instructor_id=instructor1.id)
        class2 = Class(course_name="Mat 101", section="H002", instructor_id=instructor2.id)
        class3 = Class(course_name="Mat 101", section="H003", instructor_id=instructor3.id)

        db.session.add_all([class1, class2, class3])
        db.session.commit()

        # ---------------------------
        # Create Students
        # ---------------------------
        student1 = Student(name="John Doe", student_id="W1001", class_id=class1.id, is_authorized=True)
        student2 = Student(name="Jane Smith", student_id="W1002", class_id=class1.id, is_authorized=True)
        student3 = Student(name="Emily Davis", student_id="W1003", class_id=class2.id, is_authorized=False)
        student4 = Student(name="Michael Brown", student_id="W1004", class_id=class3.id, is_authorized=True)
        student5 = Student(name="Sarah Wilson", student_id="W1005", class_id=class3.id, is_authorized=False)

        db.session.add_all([student1, student2, student3, student4, student5])
        db.session.commit()

        # ---------------------------
        # Create RetakeSchedules
        # ---------------------------
        # Define available retake dates and times
        retake_schedules = [
            RetakeSchedule(date="2025-02-10", time="09:00", max_capacity=5, current_bookings=0),
            RetakeSchedule(date="2025-02-10", time="11:00", max_capacity=5, current_bookings=0),
            RetakeSchedule(date="2025-02-11", time="14:00", max_capacity=5, current_bookings=0),
            RetakeSchedule(date="2025-02-12", time="10:00", max_capacity=5, current_bookings=0),
            RetakeSchedule(date="2025-02-12", time="16:00", max_capacity=5, current_bookings=0),
        ]

        db.session.add_all(retake_schedules)
        db.session.commit()

        # ---------------------------
        # Create Retakes
        # ---------------------------
        # Schedule retakes for students
        # Ensure that retakes do not exceed the max_capacity
        # We'll assign retakes to students who are authorized

        # Define a helper function to find a RetakeSchedule
        def find_schedule(date, time_str):
            return RetakeSchedule.query.filter_by(date=date, time=time_str).first()

        # Assign Retakes
        retake1_schedule = find_schedule("2025-02-10", "09:00")
        retake2_schedule = find_schedule("2025-02-10", "11:00")
        retake3_schedule = find_schedule("2025-02-11", "14:00")

        retakes = [
            Retake(student_id=student1.id, date=retake1_schedule.date, time=retake1_schedule.time, status="Scheduled"),
            Retake(student_id=student2.id, date=retake1_schedule.date, time=retake1_schedule.time, status="Scheduled"),
            Retake(student_id=student4.id, date=retake2_schedule.date, time=retake2_schedule.time, status="Scheduled"),
            # student5 is not authorized; optionally, handle differently or skip
        ]

        # Update current_bookings
        for retake in retakes:
            schedule = find_schedule(retake.date, retake.time)
            if schedule and schedule.current_bookings < schedule.max_capacity:
                schedule.current_bookings += 1
                db.session.add(retake)
            else:
                print(f"Cannot schedule retake for student_id {retake.student_id} on {retake.date} at {retake.time}: Capacity reached.")

        db.session.commit()

        print("Sample data has been successfully added to the database.")

if __name__ == "__main__":
    seed_data()
