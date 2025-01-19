from datetime import datetime, timedelta
from config import available_schedule

def generate_schedule():
    today = datetime.now()
    schedule = []

    for i in range(7):  # Look ahead 7 days
        date = today + timedelta(days=i)
        day_name = date.strftime("%A")

        if day_name in available_schedule:
            for time in available_schedule[day_name]:
                schedule.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "time": time
                })

    return schedule
