"""
Calculate team stats from matches data
"""
from app.database import SessionLocal
from app.models import Event, Match, EventTeamStat
from sqlalchemy import select, func
from collections import defaultdict


def calculate_team_stats_for_event(event_id: int):
    """Calculate team statistics from match results"""

    db = SessionLocal()

    try:
        # Get all matches for this event
        matches_stmt = select(Match).where(
            Match.event_id == event_id,
            Match.status == 'finished',
            Match.team1_score.isnot(None),
            Match.team2_score.isnot(None)
        )
        matches = db.execute(matches_stmt).scalars().all()

        print(f"📊 Found {len(matches)} finished matches")

        # Aggregate stats by team
        team_stats = defaultdict(lambda: {
            'wins': 0,
            'losses': 0,
            'maps_played': 0,
            'logo': None
        })

        for match in matches:
            # Team 1
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
        print(f"\n💾 Saving stats for {len(team_stats)} teams...")

        for team_name, stats in team_stats.items():
            total_games = stats['wins'] + stats['losses']
            win_rate = (stats['wins'] / total_games * 100) if total_games > 0 else 0

            # Check if exists
            existing = db.query(EventTeamStat).filter(
                EventTeamStat.event_id == event_id,
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
                    event_id=event_id,
                    team_name=team_name,
                    team_logo=stats['logo'],
                    wins=stats['wins'],
                    losses=stats['losses'],
                    win_rate=round(win_rate, 2),
                    maps_played=stats['maps_played']
                )
                db.add(team_stat)

            print(f"  {team_name}: {stats['wins']}W {stats['losses']}L ({win_rate:.1f}%)")

        db.commit()
        print(f"\n✅ Team stats calculated and saved!")

    finally:
        db.close()


if __name__ == "__main__":
    # Budapest Major event internal ID
    event_id = 13  # From database

    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).first()
    db.close()

    if event:
        print(f"📌 Calculating stats for: {event.name}\n")
        calculate_team_stats_for_event(event_id)
    else:
        print(f"❌ Event not found with id={event_id}")
