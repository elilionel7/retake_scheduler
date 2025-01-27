from app import create_app
from app import db 
from app.models import Instructor, Class, Student

app = create_app()

def populate_sample_data():
    with app.app_context():
        # Clear existing data (optional, only if you want a clean slate)
        db.drop_all()
        db.create_all()

        # Add sample instructors
        instructors = [
            Instructor(name="Dr. Lio Eli", email="w10019429@usm.edu"),
            Instructor(name="Prof. Sam Lio", email="saml@example.com")
        ]
        db.session.add_all(instructors)
        db.session.commit()

        # Add sample classes
        classes = [
            Class(course_name="MAT 101", section="H001", instructor_id=instructors[0].id),
            Class(course_name="MAT 101", section="H002", instructor_id=instructors[1].id),
        ]
        db.session.add_all(classes)
        db.session.commit()

        # Add sample students
        students = [
            Student(name="Alice Johnson", student_id="W1001", class_id=classes[0].id, is_authorized=True),
            Student(name="Bob Williams", student_id="W1002", class_id=classes[1].id, is_authorized=False),
            Student(name="Charlie Brown", student_id="W1003", class_id=classes[0].id, is_authorized=True),
            Student(name="David Lee", student_id="W1004", class_id=classes[1].id, is_authorized=False), 
            Student(name="Eva Davis", student_id="W1005", class_id=classes[0].id, is_authorized=True),
        ]
        db.session.add_all(students)
        db.session.commit()

        print("Sample data populated successfully!")

if __name__ == "__main__":
    populate_sample_data()
