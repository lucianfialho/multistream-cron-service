"""
Quick script to update Budapest Major status to 'finished'
Run with: python update_budapest_status.py
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get DATABASE_URL from Railway environment or .env
# You'll need to set this in Railway or pass it as env var
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not set. Set it via environment variable.")
    print("   Example: export DATABASE_URL='postgresql://user:pass@host/db'")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Update Budapest Major to finished
    result = session.execute(
        text("""
            UPDATE events
            SET status = 'finished',
                start_date = '2024-12-13',
                end_date = '2024-12-16',
                updated_at = NOW()
            WHERE slug = 'starladder-budapest-major-2025'
            RETURNING id, name, status;
        """)
    )

    session.commit()

    event = result.fetchone()
    if event:
        print(f"✅ Updated event: {event.name}")
        print(f"   Status: {event.status}")
        print(f"   ID: {event.id}")
    else:
        print("❌ Event not found")

except Exception as e:
    session.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    session.close()
