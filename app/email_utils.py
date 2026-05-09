from flask_mail import Message
from .extensions import mail


def _student_email(student):
    return f"{student.student_id}@usm.edu"


def send_booking_confirmation(student, retake):
    msg = Message(
        subject="Retake Scheduled – Confirmation",
        recipients=[_student_email(student)],
        body=(
            f"Hi {student.name},\n\n"
            f"Your retake has been successfully scheduled.\n\n"
            f"  Date: {retake.date}\n"
            f"  Time: {retake.time}\n\n"
            f"Please attend on time. Missing this appointment will count as one of your allowed attempts.\n\n"
            f"Retake Scheduler"
        ),
    )
    mail.send(msg)


def send_reminder(student, retake):
    msg = Message(
        subject="Reminder: Your Retake Is Tomorrow",
        recipients=[_student_email(student)],
        body=(
            f"Hi {student.name},\n\n"
            f"This is a reminder that your retake is scheduled for tomorrow.\n\n"
            f"  Date: {retake.date}\n"
            f"  Time: {retake.time}\n\n"
            f"Missing this appointment without cancelling beforehand will count as a used attempt.\n\n"
            f"Retake Scheduler"
        ),
    )
    mail.send(msg)


def send_slot_cancelled(student, retake):
    msg = Message(
        subject="Retake Slot Cancelled – Please Rebook",
        recipients=[_student_email(student)],
        body=(
            f"Hi {student.name},\n\n"
            f"Your retake slot on {retake.date} at {retake.time} has been cancelled by your instructor.\n\n"
            f"This does not count against your attempts. Please log in and choose a new slot before your deadline.\n\n"
            f"  Deadline: {student.authorization_deadline}\n\n"
            f"Retake Scheduler"
        ),
    )
    mail.send(msg)


def send_ineligible_notice(student):
    msg = Message(
        subject="Retake Eligibility Removed",
        recipients=[_student_email(student)],
        body=(
            f"Hi {student.name},\n\n"
            f"You have used all of your allowed retake attempts and are no longer eligible to schedule a retake.\n\n"
            f"Please contact your instructor if you have questions.\n\n"
            f"Retake Scheduler"
        ),
    )
    mail.send(msg)
