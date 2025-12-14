"""
Scraper for HLTV Player Stats
URL: https://www.hltv.org/stats/players?event={event_id}
"""
from .base import BaseScraper
from typing import List, Dict, Optional
import sys
import re


class StatsPlayersScraper(BaseScraper):
    """Scrape player statistics from /stats/players page"""

    def scrape(self, event_id: str) -> List[Dict]:
        """
        Scrape player stats for a specific event

        Args:
            event_id: HLTV event ID

        Returns:
            List of player stat dictionaries
        """
        url = f"{self.base_url}/stats/players?event={event_id}"
        soup = self.fetch(url)

        if not soup:
            print(f"❌ Failed to fetch player stats for event {event_id}", file=sys.stderr)
            return []

        players = []

        # Find the stats table
        stats_table = soup.find('table', class_='stats-table')

        if not stats_table:
            print(f"⚠️  No stats table found for event {event_id}", file=sys.stderr)
            return []

        # Find all player rows (tbody tr)
        tbody = stats_table.find('tbody')
        if not tbody:
            print(f"⚠️  No tbody found in stats table", file=sys.stderr)
            return []

        rows = tbody.find_all('tr')
        print(f"📊 Found {len(rows)} player rows for event {event_id}", file=sys.stderr)

        for row in rows:
            try:
                player = self._parse_player_row(row, event_id)
                if player:
                    players.append(player)
            except Exception as e:
                print(f"⚠️  Error parsing player row: {e}", file=sys.stderr)
                continue

        print(f"✅ Parsed {len(players)} player stats", file=sys.stderr)
        return players

    def _parse_player_row(self, row, event_id: str) -> Optional[Dict]:
        """Parse a single player statistics row"""

        cells = row.find_all('td')

        if len(cells) < 7:
            return None

        # Player name (cell 0)
        player_name = None
        player_cell = cells[0].find('a', class_='playerCol')
        if player_cell:
            player_name = player_cell.text.strip()

        if not player_name:
            return None

        # Team name (cell 1)
        team_name = None
        team_cell = cells[1].find('a')
        if team_cell:
            team_name = team_cell.text.strip()

        # Maps played (cell 2)
        maps_played = None
        try:
            maps_played = int(cells[2].text.strip())
        except:
            pass

        # K-D Diff (cell 3) - skip

        # K-D Ratio (cell 4)
        kd_ratio = None
        try:
            kd_ratio = float(cells[4].text.strip())
        except:
            pass

        # Rating (cell 5)
        rating = None
        try:
            rating = float(cells[5].text.strip())
        except:
            pass

        return {
            'event_id': event_id,
            'player_name': player_name,
            'team_name': team_name,
            'kills': None,  # Not in this table
            'deaths': None,  # Not in this table
            'rating': rating,
            'hs_percent': None,  # Not in this table
            'kd_ratio': kd_ratio,
            'maps_played': maps_played
        }
