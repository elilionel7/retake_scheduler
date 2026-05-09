from datetime import timedelta

def add_business_days(start_date, days):
    """Advance start_date by N business days (Mon–Fri)."""
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current
