"""
Scraper for HLTV Results page
URL: https://www.hltv.org/results?event={event_id}
"""
from .base import BaseScraper
from typing import List, Dict, Optional
from datetime import datetime
import sys
import re


def upgrade_logo_quality(logo_url: str) -> str:
    """
    Upgrade logo URL from low quality (w=50) to high quality (w=200)

    Examples:
    - w=50 -> w=200 (better quality, colored)
    - Keeps other parameters intact
    """
    if not logo_url:
        return logo_url

    # Replace w=50 with w=200 for higher quality logos
    return logo_url.replace('w=50', 'w=200')


class StatsMatchesScraper(BaseScraper):
    """Scrape matches from /results page"""

    def scrape(self, event_id: str) -> List[Dict]:
        url = f"{self.base_url}/results?event={event_id}"
        soup = self.fetch(url)

        if not soup:
            print(f"❌ Failed to fetch matches for event {event_id}", file=sys.stderr)
            return []

        matches = []
        result_containers = soup.find_all('div', class_='result-con')
        print(f"📊 Found {len(result_containers)} match containers for event {event_id}", file=sys.stderr)

        for container in result_containers:
            try:
                match = self._parse_match_container(container, event_id)
                if match:
                    matches.append(match)
            except Exception as e:
                print(f"⚠️  Error parsing match: {e}", file=sys.stderr)
                continue

        print(f"✅ Parsed {len(matches)} matches", file=sys.stderr)
        return matches

    def _parse_match_container(self, container, event_id: str) -> Optional[Dict]:
        """Parse a single match container from /results page"""

        match_link = container.find('a', class_='a-reset')
        if not match_link:
            return None

        href = match_link.get('href', '')
        match_id_match = re.search(r'/matches/(\d+)/', href)
        if not match_id_match:
            return None

        external_id = match_id_match.group(1)

        # Find team cells
        team_cells = container.find_all('td', class_='team-cell')

        team1_name = None
        team1_logo = None
        team2_name = None
        team2_logo = None

        if len(team_cells) >= 2:
            team1_div = team_cells[0].find('div', class_='team')
            if team1_div:
                team1_name = team1_div.text.strip()
            team1_img = team_cells[0].find('img', class_='team-logo')
            if team1_img:
                team1_logo = upgrade_logo_quality(team1_img.get('src'))

            team2_div = team_cells[1].find('div', class_='team')
            if team2_div:
                team2_name = team2_div.text.strip()
            team2_img = team_cells[1].find('img', class_='team-logo')
            if team2_img:
                team2_logo = upgrade_logo_quality(team2_img.get('src'))

        # Find score
        team1_score = None
        team2_score = None

        score_cell = container.find('td', class_='result-score')
        if score_cell:
            scores = score_cell.find_all('span')
            if len(scores) >= 2:
                try:
                    team1_score = int(scores[0].text.strip())
                    team2_score = int(scores[1].text.strip())
                except:
                    pass

        # Extract date from data attribute
        match_date = None
        date_unix = container.get('data-zonedgrouping-entry-unix')
        if date_unix:
            try:
                match_date = datetime.fromtimestamp(int(date_unix) / 1000)
            except:
                pass

        # Map name
        match_map = None
        map_div = container.find('div', class_='map-text')
        if map_div:
            map_text = map_div.text.strip()
            if map_text and map_text not in ['bo1', 'bo3', 'bo5']:
                match_map = map_text

        status = 'finished' if team1_score is not None else 'upcoming'

        return {
            'external_id': external_id,
            'event_id': event_id,
            'team1_name': team1_name,
            'team1_logo': team1_logo,
            'team2_name': team2_name,
            'team2_logo': team2_logo,
            'team1_score': team1_score,
            'team2_score': team2_score,
            'date': match_date,
            'map': match_map,
            'status': status
        }
