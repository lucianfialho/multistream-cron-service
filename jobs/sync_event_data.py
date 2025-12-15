"""
Event data synchronization jobs
"""
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Event, Match
from scrapers.base import BaseScraper
from scrapers.stats_events import StatsEventsScraper
from scrapers.stats_matches import StatsMatchesScraper


def sync_all_event_matches():
    """Sync matches for all active events (ongoing or upcoming)"""
    db = SessionLocal()

    try:
        # Get all events that are not finished
        stmt = select(Event).where(Event.status.in_(['upcoming', 'ongoing']))
        events = db.execute(stmt).scalars().all()

        print(f"📊 Found {len(events)} active events to sync", file=sys.stderr)

        total_new = 0
        total_updated = 0

        for event in events:
            print(f"\n🔄 Syncing matches for event: {event.name} (ID: {event.external_id})", file=sys.stderr)

            # Scrape matches for this event
            scraper = StatsMatchesScraper()
            matches_data = scraper.scrape(event.external_id)

            print(f"  📥 Scraped {len(matches_data)} matches from HLTV", file=sys.stderr)

            new_matches = 0
            updated_matches = 0

            for match_data in matches_data:
                # Check if match already exists
                existing_match = db.query(Match).filter(
                    Match.external_id == match_data['external_id']
                ).first()

                if existing_match:
                    # Update existing match
                    existing_match.team1_name = match_data.get('team1_name')
                    existing_match.team1_logo = match_data.get('team1_logo')
                    existing_match.team2_name = match_data.get('team2_name')
                    existing_match.team2_logo = match_data.get('team2_logo')
                    existing_match.team1_score = match_data.get('team1_score')
                    existing_match.team2_score = match_data.get('team2_score')
                    existing_match.date = match_data.get('date')
                    existing_match.map = match_data.get('map')
                    existing_match.status = match_data.get('status', 'upcoming')
                    existing_match.updated_at = datetime.utcnow()
                    updated_matches += 1
                else:
                    # Create new match
                    new_match = Match(
                        external_id=match_data['external_id'],
                        event_id=event.id,
                        team1_name=match_data.get('team1_name'),
                        team1_logo=match_data.get('team1_logo'),
                        team2_name=match_data.get('team2_name'),
                        team2_logo=match_data.get('team2_logo'),
                        team1_score=match_data.get('team1_score'),
                        team2_score=match_data.get('team2_score'),
                        date=match_data.get('date'),
                        map=match_data.get('map'),
                        status=match_data.get('status', 'upcoming')
                    )
                    db.add(new_match)
                    new_matches += 1

            db.commit()

            print(f"  ✅ Event {event.name}: {new_matches} new, {updated_matches} updated", file=sys.stderr)
            total_new += new_matches
            total_updated += updated_matches

        print(f"\n🎉 Sync completed: {total_new} new matches, {total_updated} updated", file=sys.stderr)

    except Exception as e:
        db.rollback()
        print(f"❌ Error syncing matches: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


def sync_events():
    """Sync new events from HLTV"""
    db = SessionLocal()

    try:
        print(f"🔄 Syncing events from HLTV", file=sys.stderr)

        # Scrape events
        scraper = StatsEventsScraper()
        events_data = scraper.scrape()

        print(f"📥 Scraped {len(events_data)} events from HLTV", file=sys.stderr)

        new_events = 0
        updated_events = 0

        for event_data in events_data:
            # Check if event already exists
            existing_event = db.query(Event).filter(
                Event.external_id == event_data['external_id']
            ).first()

            if existing_event:
                # Update existing event
                existing_event.name = event_data.get('name')
                existing_event.slug = event_data.get('slug')
                existing_event.start_date = event_data.get('start_date')
                existing_event.end_date = event_data.get('end_date')
                existing_event.type = event_data.get('type')
                existing_event.prize_pool = event_data.get('prize_pool')
                existing_event.location = event_data.get('location')
                existing_event.status = event_data.get('status', 'upcoming')
                existing_event.updated_at = datetime.utcnow()
                updated_events += 1
            else:
                # Create new event
                new_event = Event(
                    external_id=event_data['external_id'],
                    slug=event_data.get('slug'),
                    name=event_data.get('name'),
                    start_date=event_data.get('start_date'),
                    end_date=event_data.get('end_date'),
                    type=event_data.get('type'),
                    prize_pool=event_data.get('prize_pool'),
                    location=event_data.get('location'),
                    status=event_data.get('status', 'upcoming')
                )
                db.add(new_event)
                new_events += 1

        db.commit()

        print(f"✅ Events sync completed: {new_events} new, {updated_events} updated", file=sys.stderr)

    except Exception as e:
        db.rollback()
        print(f"❌ Error syncing events: {e}", file=sys.stderr)
        raise
    finally:
        db.close()
