"""
Scraper for HLTV Team Stats
URL: https://www.hltv.org/stats/teams?event={event_id}
"""
from .base import BaseScraper
from typing import List, Dict, Optional
import sys


class StatsTeamsScraper(BaseScraper):
    """Scrape team statistics from /stats/teams page"""

    def scrape(self, event_id: str) -> List[Dict]:
        """
        Scrape team stats for a specific event

        Args:
            event_id: HLTV event ID

        Returns:
            List of team stat dictionaries
        """
        url = f"{self.base_url}/stats/teams?event={event_id}"
        soup = self.fetch(url)

        if not soup:
            print(f"❌ Failed to fetch team stats for event {event_id}", file=sys.stderr)
            return []

        teams = []

        # Find the stats table
        stats_table = soup.find('table', class_='stats-table')

        if not stats_table:
            print(f"⚠️  No stats table found for event {event_id}", file=sys.stderr)
            return []

        # Find all team rows (tbody tr)
        tbody = stats_table.find('tbody')
        if not tbody:
            print(f"⚠️  No tbody found in stats table", file=sys.stderr)
            return []

        rows = tbody.find_all('tr')
        print(f"📊 Found {len(rows)} team rows for event {event_id}", file=sys.stderr)

        for row in rows:
            try:
                team = self._parse_team_row(row, event_id)
                if team:
                    teams.append(team)
            except Exception as e:
                print(f"⚠️  Error parsing team row: {e}", file=sys.stderr)
                continue

        print(f"✅ Parsed {len(teams)} team stats", file=sys.stderr)
        return teams

    def _parse_team_row(self, row, event_id: str) -> Optional[Dict]:
        """Parse a single team statistics row"""

        cells = row.find_all('td')

        if len(cells) < 5:
            return None

        # Team name and logo (cell 0)
        team_name = None
        team_logo = None
        team_cell = cells[0].find('a', class_='teamCol')
        if team_cell:
            team_name = team_cell.text.strip()
            logo_img = team_cell.find('img')
            if logo_img:
                team_logo = logo_img.get('src')

        if not team_name:
            return None

        # Maps played (cell 1)
        maps_played = None
        try:
            maps_played = int(cells[1].text.strip())
        except:
            pass

        # Wins (cell 2)
        wins = None
        try:
            wins_text = cells[2].text.strip()
            # Format might be "13 (54.2%)"
            if '(' in wins_text:
                wins = int(wins_text.split('(')[0].strip())
            else:
                wins = int(wins_text)
        except:
            pass

        # Losses (cell 3)
        losses = None
        try:
            losses_text = cells[3].text.strip()
            # Format might be "11 (45.8%)"
            if '(' in losses_text:
                losses = int(losses_text.split('(')[0].strip())
            else:
                losses = int(losses_text)
        except:
            pass

        # Calculate win rate
        win_rate = None
        if wins is not None and losses is not None and (wins + losses) > 0:
            win_rate = (wins / (wins + losses)) * 100

        return {
            'event_id': event_id,
            'team_name': team_name,
            'team_logo': team_logo,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2) if win_rate else None,
            'maps_played': maps_played
        }
