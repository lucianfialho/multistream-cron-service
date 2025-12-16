"""
Script to update event details (prize pool, location, type) for Budapest Major
"""
import sys
from app.database import SessionLocal
from app.models import Event
from datetime import datetime

db = SessionLocal()

try:
    # Find Budapest Major
    event = db.query(Event).filter(Event.slug == 'starladder-budapest-major-2025').first()

    if event:
        print(f"Found event: {event.name}")
        
        # Update with known details for Budapest Major
        event.prize_pool = "$1,250,000"
        event.location = "Budapest, Hungary"
        event.type = "Major Championship"
        event.start_date = datetime(2024, 12, 13)
        event.end_date = datetime(2024, 12, 16)
        event.updated_at = datetime.utcnow()

        db.commit()

        print(f"\n✅ Updated event details:")
        print(f"   Prize Pool: {event.prize_pool}")
        print(f"   Location: {event.location}")
        print(f"   Type: {event.type}")
        print(f"   Dates: {event.start_date} → {event.end_date}")
    else:
        print("❌ Event not found")

except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    db.close()
