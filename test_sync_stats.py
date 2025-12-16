"""
Test script to sync player and team stats for Budapest Major
"""
import sys
from scrapers.stats_players import StatsPlayersScraper
from scrapers.stats_teams import StatsTeamsScraper
from app.database import SessionLocal
from app.models import EventPlayerStat, EventTeamStat, Event
from sqlalchemy import select

def sync_stats():
    """Sync player and team stats for Budapest Major (event_id=8042)"""

    event_id = "8042"  # Budapest Major

    db = SessionLocal()

    try:
        # Get event from database
        stmt = select(Event).where(Event.external_id == event_id)
        event = db.execute(stmt).scalar_one_or_none()

        if not event:
            print(f"❌ Event {event_id} not found in database")
            return

        print(f"📌 Syncing stats for event: {event.name} (id={event.id})")

        # Scrape players
        print("\n🔄 Scraping player stats...")
        player_scraper = StatsPlayersScraper()
        players_data = player_scraper.scrape(event_id)

        print(f"\n💾 Inserting {len(players_data)} player stats...")
        for player_data in players_data:
            # Check if exists
            existing = db.query(EventPlayerStat).filter(
                EventPlayerStat.event_id == event.id,
                EventPlayerStat.player_name == player_data['player_name']
            ).first()

            if existing:
                # Update
                existing.team_name = player_data['team_name']
                existing.rating = player_data['rating']
                existing.kd_ratio = player_data['kd_ratio']
                existing.maps_played = player_data['maps_played']
            else:
                # Insert
                stat = EventPlayerStat(
                    event_id=event.id,
                    player_name=player_data['player_name'],
                    team_name=player_data['team_name'],
                    rating=player_data['rating'],
                    kd_ratio=player_data['kd_ratio'],
                    maps_played=player_data['maps_played']
                )
                db.add(stat)

        db.commit()
        print(f"✅ Player stats saved!")

        # Scrape teams
        print("\n🔄 Scraping team stats...")
        team_scraper = StatsTeamsScraper()
        teams_data = team_scraper.scrape(event_id)

        print(f"\n💾 Inserting {len(teams_data)} team stats...")
        for team_data in teams_data:
            # Check if exists
            existing = db.query(EventTeamStat).filter(
                EventTeamStat.event_id == event.id,
                EventTeamStat.team_name == team_data['team_name']
            ).first()

            if existing:
                # Update
                existing.team_logo = team_data['team_logo']
                existing.wins = team_data['wins']
                existing.losses = team_data['losses']
                existing.win_rate = team_data['win_rate']
                existing.maps_played = team_data['maps_played']
            else:
                # Insert
                stat = EventTeamStat(
                    event_id=event.id,
                    team_name=team_data['team_name'],
                    team_logo=team_data['team_logo'],
                    wins=team_data['wins'],
                    losses=team_data['losses'],
                    win_rate=team_data['win_rate'],
                    maps_played=team_data['maps_played']
                )
                db.add(stat)

        db.commit()
        print(f"✅ Team stats saved!")

        print("\n🎉 All stats synced successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    sync_stats()
