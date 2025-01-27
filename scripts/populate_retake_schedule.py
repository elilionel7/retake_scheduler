from app import create_app,db
from app.models import RetakeSchedule

app = create_app()

with app.app_context():
    # Example: Add available slots
    slots = [
        {"date": "2025-02-15", "time": "13:00"},
        {"date": "2025-02-15", "time": "14:00"},
        {"date": "2025-02-16", "time": "15:00"},
    ]

    for slot in slots:
        new_slot = RetakeSchedule(date=slot["date"], time=slot["time"])
        db.session.add(new_slot)

    db.session.commit()
    print("Retake schedule slots have been populated.")
