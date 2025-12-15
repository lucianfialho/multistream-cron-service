"""
Scraper for HLTV Events page
URL: https://www.hltv.org/events
"""
from .base import BaseScraper
from typing import List, Dict, Optional
from datetime import datetime
import sys
import re


class StatsEventsScraper(BaseScraper):
    """Scrape upcoming and ongoing events from /events page"""

    def scrape(self) -> List[Dict]:
        """Scrape events from HLTV events page"""
        url = f"{self.base_url}/events"
        soup = self.fetch(url)

        if not soup:
            print(f"❌ Failed to fetch events", file=sys.stderr)
            return []

        events = []

        # Find all event containers
        event_containers = soup.find_all('div', class_='event-col')
        print(f"📊 Found {len(event_containers)} event containers", file=sys.stderr)

        for container in event_containers:
            try:
                event = self._parse_event_container(container)
                if event:
                    events.append(event)
            except Exception as e:
                print(f"⚠️  Error parsing event: {e}", file=sys.stderr)
                continue

        print(f"✅ Parsed {len(events)} events", file=sys.stderr)
        return events

    def _parse_event_container(self, container) -> Optional[Dict]:
        """Parse a single event container from /events page"""

        # Find event link
        event_link = container.find('a', class_='a-reset')
        if not event_link:
            return None

        href = event_link.get('href', '')

        # Extract event ID and slug from URL: /events/7148/starladder-budapest-major-2025
        match = re.search(r'/events/(\d+)/([^/]+)', href)
        if not match:
            return None

        external_id = match.group(1)
        slug = match.group(2)

        # Event name
        name_elem = container.find('div', class_='text-ellipsis')
        name = name_elem.text.strip() if name_elem else None

        # Date range
        date_elem = container.find('span', class_='eventdate')
        start_date = None
        end_date = None
        if date_elem:
            date_text = date_elem.text.strip()
            # TODO: Parse date range (format: "Dec 13 - Dec 16")
            # For now, leave as None - can be enhanced later

        # Prize pool
        prize_elem = container.find('div', class_='prizePoolEllipsis')
        prize_pool = prize_elem.text.strip() if prize_elem else None

        # Location
        location_elem = container.find('span', class_='big-event-location')
        location = location_elem.text.strip() if location_elem else None

        # Event type (major, premier, etc.)
        type_elem = container.find('div', class_='eventTeamName')
        event_type = type_elem.text.strip() if type_elem else None

        # Determine status based on container class or position
        status = 'upcoming'
        if container.find_parent('div', class_='tab-content'):
            # Could check if in "Ongoing events" or "Upcoming events" tab
            status = 'upcoming'

        return {
            'external_id': external_id,
            'slug': slug,
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
            'type': event_type,
            'prize_pool': prize_pool,
            'location': location,
            'status': status
        }
