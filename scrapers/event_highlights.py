"""
Scraper for HLTV Event Highlights
URL: https://www.hltv.org/events/{event_id}/{event_slug}
"""
from .base import BaseScraper
from typing import List, Dict, Optional
import sys
import re


class EventHighlightsScraper(BaseScraper):
    """Scrape highlights/clips from event page"""

    def scrape(self, event_id: str) -> List[Dict]:
        """
        Scrape highlights from event page

        Args:
            event_id: HLTV event ID (e.g., "8042")

        Returns:
            List of highlights with title, url, thumbnail, etc.
        """
        # Build URL - we'll try common patterns
        url = f"{self.base_url}/events/{event_id}/starladder-budapest-major-2025"
        soup = self.fetch(url)

        if not soup:
            print(f"❌ Failed to fetch event page for {event_id}", file=sys.stderr)
            return []

        highlights = []

        # Find highlights section
        highlights_section = soup.find('div', class_='event-highlights')

        if not highlights_section:
            print(f"⚠️  No highlights section found for event {event_id}", file=sys.stderr)
            return []

        print(f"✅ Found highlights section for event {event_id}", file=sys.stderr)

        # Find all highlight items
        highlight_items = highlights_section.find_all('a', class_='highlight-item')

        if not highlight_items:
            # Try alternative selectors
            highlight_items = highlights_section.find_all('div', class_='highlight')

        print(f"📺 Found {len(highlight_items)} highlight items", file=sys.stderr)

        for item in highlight_items:
            try:
                highlight = self._parse_highlight(item)
                if highlight:
                    highlights.append(highlight)
            except Exception as e:
                print(f"⚠️  Error parsing highlight: {e}", file=sys.stderr)
                continue

        return highlights

    def _parse_highlight(self, item) -> Optional[Dict]:
        """Parse a single highlight item"""

        # Get link
        url = item.get('href') if item.name == 'a' else None
        if url and not url.startswith('http'):
            url = f"{self.base_url}{url}"

        # Get title
        title_elem = item.find('div', class_='highlight-title') or item.find('span', class_='text')
        title = title_elem.text.strip() if title_elem else None

        # Get thumbnail
        img_elem = item.find('img')
        thumbnail = img_elem.get('src') if img_elem else None

        # Get video ID if it's YouTube
        video_id = None
        if url and ('youtube.com' in url or 'youtu.be' in url):
            if 'youtu.be' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
            elif 'v=' in url:
                video_id = url.split('v=')[1].split('&')[0]

        # Get duration if available
        duration_elem = item.find('div', class_='duration') or item.find('span', class_='duration')
        duration = duration_elem.text.strip() if duration_elem else None

        if not url:
            return None

        return {
            'title': title,
            'url': url,
            'thumbnail': thumbnail,
            'video_id': video_id,
            'duration': duration,
            'platform': 'youtube' if video_id else 'other'
        }
