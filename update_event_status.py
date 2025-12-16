"""
Script to update Budapest Major event status to 'finished'
"""
from app.database import SessionLocal
from app.models import Event
from datetime import datetime

db = SessionLocal()

try:
    # Find Budapest Major event
    event = db.query(Event).filter(Event.slug == 'starladder-budapest-major-2025').first()

    if event:
        print(f"Found event: {event.name}")
        print(f"Current status: {event.status}")
        print(f"Current dates: {event.start_date} -> {event.end_date}")

        # Update status to finished
        event.status = 'finished'
        event.updated_at = datetime.utcnow()

        # Also set dates if missing (Budapest Major was Dec 13-16, 2024)
        if not event.start_date:
            event.start_date = datetime(2024, 12, 13)
        if not event.end_date:
            event.end_date = datetime(2024, 12, 16)

        db.commit()

        print(f"\n✅ Updated event status to: {event.status}")
        print(f"   Dates: {event.start_date} -> {event.end_date}")
    else:
        print("❌ Event not found")

finally:
    db.close()
