from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models import Event, Match, EventPlayerStat, EventTeamStat
from collections import defaultdict
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(tags=["events"])


class UpdateEventStatusRequest(BaseModel):
    status: str  # upcoming, ongoing, finished

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
def get_event_overlay(
    slug: str,
    matches_limit: int = 100,
    players_limit: int = 20,
    teams_limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get complete event data: event + matches + top players + top teams

    Query params:
    - matches_limit: Max number of matches to return (default: 100)
    - players_limit: Max number of players to return (default: 20)
    - teams_limit: Max number of teams to return (default: 20)
    """

    # Get event
    stmt = select(Event).where(Event.slug == slug)
    event = db.execute(stmt).scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get matches (limit configurable, max 500)
    max_matches = min(matches_limit, 500)
    matches_stmt = (
        select(Match)
        .where(Match.event_id == event.id)
        .order_by(Match.date.desc())
        .limit(max_matches)
    )
    matches = db.execute(matches_stmt).scalars().all()

    # Get player stats (limit configurable, max 100)
    max_players = min(players_limit, 100)
    players_stmt = (
        select(EventPlayerStat)
        .where(EventPlayerStat.event_id == event.id)
        .order_by(EventPlayerStat.rating.desc())
        .limit(max_players)
    )
    player_stats = db.execute(players_stmt).scalars().all()

    # Get team stats (limit configurable, max 50)
    max_teams = min(teams_limit, 50)
    teams_stmt = (
        select(EventTeamStat)
        .where(EventTeamStat.event_id == event.id)
        .order_by(EventTeamStat.win_rate.desc())
        .limit(max_teams)
    )
    team_stats = db.execute(teams_stmt).scalars().all()

    return {
        "event": {
            "id": event.id,
            "external_id": event.external_id,
            "slug": event.slug,
            "name": event.name,
            "status": event.status,
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

@router.post("/events/{slug}/calculate-stats")
def calculate_event_stats(slug: str, db: Session = Depends(get_db)):
    """Calculate team statistics from match results"""

    # Get event
    stmt = select(Event).where(Event.slug == slug)
    event = db.execute(stmt).scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get all finished matches
    matches_stmt = select(Match).where(
        Match.event_id == event.id,
        Match.status == 'finished',
        Match.team1_score.isnot(None),
        Match.team2_score.isnot(None)
    )
    matches = db.execute(matches_stmt).scalars().all()

    # Aggregate stats by team
    team_stats = defaultdict(lambda: {
        'wins': 0,
        'losses': 0,
        'maps_played': 0,
        'logo': None
    })

    for match in matches:
        team1 = match.team1_name
        team2 = match.team2_name

        if not team1 or not team2:
            continue

        # Update maps played
        team_stats[team1]['maps_played'] += 1
        team_stats[team2]['maps_played'] += 1

        # Update logos
        if match.team1_logo:
            team_stats[team1]['logo'] = match.team1_logo
        if match.team2_logo:
            team_stats[team2]['logo'] = match.team2_logo

        # Determine winner
        if match.team1_score > match.team2_score:
            team_stats[team1]['wins'] += 1
            team_stats[team2]['losses'] += 1
        elif match.team2_score > match.team1_score:
            team_stats[team2]['wins'] += 1
            team_stats[team1]['losses'] += 1

    # Save to database
    for team_name, stats in team_stats.items():
        total_games = stats['wins'] + stats['losses']
        win_rate = (stats['wins'] / total_games * 100) if total_games > 0 else 0

        # Check if exists
        existing = db.query(EventTeamStat).filter(
            EventTeamStat.event_id == event.id,
            EventTeamStat.team_name == team_name
        ).first()

        if existing:
            existing.wins = stats['wins']
            existing.losses = stats['losses']
            existing.win_rate = round(win_rate, 2)
            existing.maps_played = stats['maps_played']
            existing.team_logo = stats['logo']
        else:
            team_stat = EventTeamStat(
                event_id=event.id,
                team_name=team_name,
                team_logo=stats['logo'],
                wins=stats['wins'],
                losses=stats['losses'],
                win_rate=round(win_rate, 2),
                maps_played=stats['maps_played']
            )
            db.add(team_stat)

    db.commit()

    return {
        "status": "success",
        "message": f"Calculated stats for {len(team_stats)} teams",
        "teams": len(team_stats),
        "matches": len(matches)
    }


@router.post("/events/{slug}/update-status")
def update_event_status(slug: str, request: UpdateEventStatusRequest, db: Session = Depends(get_db)):
    """Update event status (upcoming, ongoing, finished)"""

    # Get event
    stmt = select(Event).where(Event.slug == slug)
    event = db.execute(stmt).scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Validate status
    valid_statuses = ['upcoming', 'ongoing', 'finished']
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    old_status = event.status
    event.status = request.status
    event.updated_at = datetime.utcnow()

    db.commit()

    return {
        "status": "success",
        "message": f"Event status updated from '{old_status}' to '{request.status}'",
        "event": {
            "id": event.id,
            "slug": event.slug,
            "name": event.name,
            "status": event.status
        }
    }
