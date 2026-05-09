from datetime import datetime, timedelta


def send_reminders():
    """Runs hourly. Sends a 24-hour reminder for every retake scheduled tomorrow."""
    from .extensions import db
    from .models import Retake
    from .email_utils import send_reminder

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    due = Retake.query.filter_by(date=tomorrow, status="scheduled", reminder_sent=False).all()

    for retake in due:
        try:
            send_reminder(retake.student, retake)
            retake.reminder_sent = True
        except Exception:
            pass

    db.session.commit()


def register_jobs(scheduler):
    scheduler.add_job(
        id="send_reminders",
        func=send_reminders,
        trigger="interval",
        hours=1,
        misfire_grace_time=900,
    )
