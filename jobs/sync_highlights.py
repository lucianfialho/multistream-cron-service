"""
Job to sync event highlights from HLTV
"""
from scrapers.event_highlights import EventHighlightsScraper
from app.models import Event, EventHighlight
from app.database import SessionLocal


def sync_event_highlights(event_id: str = "8042", event_slug: str = "starladder-budapest-major-2025"):
    """
    Sync highlights for a specific event

    Args:
        event_id: HLTV event ID (default: Budapest Major)
        event_slug: Event URL slug
    """
    db = SessionLocal()
    try:
        # Find event in database
        event = db.query(Event).filter(Event.external_id == event_id).first()
        if not event:
            print(f"❌ Event {event_id} not found in database")
            return

        # Scrape highlights
        scraper = EventHighlightsScraper()
        highlights = scraper.scrape(event_id, event_slug)

        if not highlights:
            print(f"⚠️  No highlights found for event {event_id}")
            return

        # Delete existing highlights for this event
        deleted_count = db.query(EventHighlight).filter(
            EventHighlight.event_id == event.id
        ).delete()

        if deleted_count > 0:
            print(f"🗑️  Deleted {deleted_count} existing highlights")

        # Insert new highlights
        for h in highlights:
            highlight = EventHighlight(
                event_id=event.id,
                title=h.get('title'),
                url=h['url'],
                embed_url=h.get('embed_url'),
                thumbnail=h.get('thumbnail'),
                video_id=h.get('video_id'),
                duration=h.get('duration'),
                platform=h.get('platform', 'twitch'),
                view_count=h.get('view_count'),
                highlight_id=h.get('highlight_id')
            )
            db.add(highlight)

        db.commit()
        print(f"✅ Synced {len(highlights)} highlights for {event.name}")
        print(f"   Platform: {highlights[0].get('platform') if highlights else 'N/A'}")
        print(f"   Top highlight: {highlights[0].get('title')[:60] if highlights else 'N/A'}...")

    except Exception as e:
        print(f"❌ Error syncing highlights: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # For manual testing
    import sys

    if len(sys.argv) > 1:
        event_id = sys.argv[1]
        event_slug = sys.argv[2] if len(sys.argv) > 2 else None
        sync_event_highlights(event_id, event_slug)
    else:
        # Default: Budapest Major
        sync_event_highlights()
