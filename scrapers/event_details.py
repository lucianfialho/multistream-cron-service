"""
Scraper for individual HLTV Event page
URL: https://www.hltv.org/events/{event_id}/{event_slug}
"""
from .base import BaseScraper
from typing import Dict, Optional
import sys
import re


class EventDetailsScraper(BaseScraper):
    """Scrape detailed information from individual event page"""

    def scrape(self, event_id: str) -> Optional[Dict]:
        """
        Scrape event details from individual event page

        Args:
            event_id: HLTV event ID (e.g., "8042")

        Returns:
            Dict with event details or None if failed
        """
        # Try to construct URL - we need the slug
        # For now, we'll scrape from /events/{event_id}/matches which works without slug
        url = f"{self.base_url}/events/{event_id}/matches"
        soup = self.fetch(url)

        if not soup:
            print(f"❌ Failed to fetch event details for {event_id}", file=sys.stderr)
            return None

        try:
            details = {}

            # Event name
            name_elem = soup.find('h1', class_='event-hub-title')
            if name_elem:
                details['name'] = name_elem.text.strip()

            # Prize pool
            prize_elem = soup.find('td', string=re.compile(r'Prize pool', re.I))
            if prize_elem:
                prize_value = prize_elem.find_next_sibling('td')
                if prize_value:
                    details['prize_pool'] = prize_value.text.strip()

            # Location
            location_elem = soup.find('td', string=re.compile(r'Location', re.I))
            if location_elem:
                location_value = location_elem.find_next_sibling('td')
                if location_value:
                    details['location'] = location_value.text.strip()

            # Event type
            type_elem = soup.find('td', string=re.compile(r'Type', re.I))
            if type_elem:
                type_value = type_elem.find_next_sibling('td')
                if type_value:
                    details['type'] = type_value.text.strip()

            # Dates
            date_elem = soup.find('td', string=re.compile(r'Dates', re.I))
            if date_elem:
                date_value = date_elem.find_next_sibling('td')
                if date_value:
                    date_text = date_value.text.strip()
                    # TODO: Parse dates (format: "13th - 16th of December 2024")
                    details['date_text'] = date_text

            # Teams count
            teams_elem = soup.find('td', string=re.compile(r'Teams', re.I))
            if teams_elem:
                teams_value = teams_elem.find_next_sibling('td')
                if teams_value:
                    teams_count = teams_value.text.strip()
                    try:
                        details['teams_count'] = int(teams_count)
                    except:
                        pass

            print(f"✅ Scraped details for event {event_id}: {details.get('name', 'Unknown')}", file=sys.stderr)
            return details

        except Exception as e:
            print(f"❌ Error parsing event details: {e}", file=sys.stderr)
            return None
