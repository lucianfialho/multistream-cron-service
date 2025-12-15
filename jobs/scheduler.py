"""
APScheduler configuration and job management
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def sync_matches_job():
    """Job to sync matches for all active events"""
    from .sync_event_data import sync_all_event_matches

    logger.info(f"[CRON] Starting match sync job at {datetime.utcnow()}")
    try:
        sync_all_event_matches()
        logger.info("[CRON] Match sync completed successfully")
    except Exception as e:
        logger.error(f"[CRON] Match sync failed: {e}", exc_info=True)


def sync_events_job():
    """Job to sync new events"""
    from .sync_event_data import sync_events

    logger.info(f"[CRON] Starting events sync job at {datetime.utcnow()}")
    try:
        sync_events()
        logger.info("[CRON] Events sync completed successfully")
    except Exception as e:
        logger.error(f"[CRON] Events sync failed: {e}", exc_info=True)


def sync_highlights_job():
    """Job to sync highlights for ongoing and recently finished events"""
    from .sync_highlights import sync_event_highlights
    from app.models import Event
    from app.database import SessionLocal
    from sqlalchemy import select, or_
    from datetime import datetime, timedelta

    logger.info(f"[CRON] Starting highlights sync job at {datetime.utcnow()}")

    db = SessionLocal()
    try:
        # Get ongoing events and recently finished events (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        stmt = select(Event).where(
            or_(
                Event.status == 'ongoing',
                Event.status == 'finished'
            ),
            Event.end_date >= seven_days_ago
        )
        events = db.execute(stmt).scalars().all()

        logger.info(f"[CRON] Found {len(events)} events to sync highlights")

        synced_count = 0
        for event in events:
            try:
                logger.info(f"[CRON] Syncing highlights for: {event.name} (ID: {event.external_id})")
                sync_event_highlights(event.external_id, event.slug)
                synced_count += 1
            except Exception as e:
                logger.error(f"[CRON] Failed to sync highlights for {event.name}: {e}")
                continue

        logger.info(f"[CRON] Highlights sync completed: {synced_count}/{len(events)} events synced")

    except Exception as e:
        logger.error(f"[CRON] Highlights sync job failed: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler():
    """Start the APScheduler with all configured jobs"""

    # Job 1: Sync matches every 10 minutes
    scheduler.add_job(
        sync_matches_job,
        trigger=IntervalTrigger(minutes=10),
        id='sync_matches',
        name='Sync event matches',
        replace_existing=True
    )

    # Job 2: Sync new events daily at midnight UTC
    scheduler.add_job(
        sync_events_job,
        trigger=CronTrigger(hour=0, minute=0),
        id='sync_events',
        name='Sync events daily',
        replace_existing=True
    )

    # Job 3: Sync highlights daily at 04:00 UTC
    scheduler.add_job(
        sync_highlights_job,
        trigger=CronTrigger(hour=4, minute=0),
        id='sync_highlights',
        name='Sync event highlights',
        replace_existing=True
    )

    scheduler.start()
    logger.info("✅ APScheduler started with jobs:")
    logger.info("  - sync_matches: Every 10 minutes")
    logger.info("  - sync_events: Daily at 00:00 UTC")
    logger.info("  - sync_highlights: Daily at 04:00 UTC")


def shutdown_scheduler():
    """Gracefully shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shut down")
