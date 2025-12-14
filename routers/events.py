from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models import Event

router = APIRouter(tags=["events"])

@router.get("/events")
def list_events(db: Session = Depends(get_db)):
    stmt = select(Event).order_by(Event.start_date.desc()).limit(50)
    events = db.execute(stmt).scalars().all()
    
    return {
        "total": len(events),
        "events": [
            {
                "id": event.id,
                "external_id": event.external_id,
                "slug": event.slug,
                "name": event.name,
                "start_date": event.start_date.isoformat() if event.start_date else None,
                "end_date": event.end_date.isoformat() if event.end_date else None,
                "type": event.type,
                "prize_pool": event.prize_pool,
                "location": event.location
            }
            for event in events
        ]
    }

@router.get("/events/{slug}")
def get_event(slug: str, db: Session = Depends(get_db)):
    stmt = select(Event).where(Event.slug == slug)
    event = db.execute(stmt).scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {
        "id": event.id,
        "external_id": event.external_id,
        "slug": event.slug,
        "name": event.name,
        "start_date": event.start_date.isoformat() if event.start_date else None,
        "end_date": event.end_date.isoformat() if event.end_date else None,
        "type": event.type,
        "prize_pool": event.prize_pool,
        "location": event.location
    }
