from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models import Event, Match, EventPlayerStat, EventTeamStat

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

@router.get("/events/{slug}/overlay")
def get_event_overlay(slug: str, db: Session = Depends(get_db)):
    """Get complete event data: event + matches + top players + top teams"""
    
    # Get event
    stmt = select(Event).where(Event.slug == slug)
    event = db.execute(stmt).scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get matches
    matches_stmt = select(Match).where(Match.event_id == event.id).order_by(Match.date.desc())
    matches = db.execute(matches_stmt).scalars().all()
    
    # Get player stats (top 10)
    players_stmt = (
        select(EventPlayerStat)
        .where(EventPlayerStat.event_id == event.id)
        .order_by(EventPlayerStat.rating.desc())
        .limit(10)
    )
    player_stats = db.execute(players_stmt).scalars().all()
    
    # Get team stats (top 10)
    teams_stmt = (
        select(EventTeamStat)
        .where(EventTeamStat.event_id == event.id)
        .order_by(EventTeamStat.win_rate.desc())
        .limit(10)
    )
    team_stats = db.execute(teams_stmt).scalars().all()
    
    return {
        "event": {
            "id": event.id,
            "external_id": event.external_id,
            "slug": event.slug,
            "name": event.name,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "type": event.type,
            "prize_pool": event.prize_pool,
            "location": event.location
        },
        "matches": [
            {
                "id": match.id,
                "external_id": match.external_id,
                "team1_name": match.team1_name,
                "team1_logo": match.team1_logo,
                "team2_name": match.team2_name,
                "team2_logo": match.team2_logo,
                "team1_score": match.team1_score,
                "team2_score": match.team2_score,
                "date": match.date.isoformat() if match.date else None,
                "map": match.map,
                "status": match.status
            }
            for match in matches
        ],
        "topPlayers": [
            {
                "player_name": player.player_name,
                "team_name": player.team_name,
                "rating": float(player.rating) if player.rating else None,
                "kd_ratio": float(player.kd_ratio) if player.kd_ratio else None,
                "maps_played": player.maps_played
            }
            for player in player_stats
        ],
        "topTeams": [
            {
                "team_name": team.team_name,
                "team_logo": team.team_logo,
                "wins": team.wins,
                "losses": team.losses,
                "win_rate": float(team.win_rate) if team.win_rate else None,
                "maps_played": team.maps_played
            }
            for team in team_stats
        ]
    }
