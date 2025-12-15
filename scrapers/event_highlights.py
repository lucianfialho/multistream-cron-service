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

    def scrape(self, event_id: str, event_slug: str = None) -> List[Dict]:
        """
        Scrape highlights from event page

        Args:
            event_id: HLTV event ID (e.g., "8042")
            event_slug: Event slug for URL (e.g., "starladder-budapest-major-2025")

        Returns:
            List of highlights with title, url, thumbnail, etc.
        """
        # Build URL - use slug if provided, otherwise try to scrape event list first
        if event_slug:
            url = f"{self.base_url}/events/{event_id}/{event_slug}"
        else:
            # Fallback - might need to be updated per event
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

        # Find all highlight video divs
        highlight_items = highlights_section.find_all('div', class_='highlight-video')

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
        """
        Parse a single highlight item (Twitch clip)

        Data attributes available:
        - data-highlight-id: Unique highlight ID
        - data-embed-url: Twitch clip embed URL
        - data-description: Clip description/title
        - data-thumbnail: Thumbnail URL
        - data-view-count: Number of views
        """

        # Get data attributes
        highlight_id = item.get('data-highlight-id')
        embed_url = item.get('data-embed-url')
        title = item.get('data-description')
        thumbnail = item.get('data-thumbnail')
        view_count = item.get('data-view-count')

        if not embed_url:
            return None

        # Extract Twitch clip ID from embed URL
        # Format: https://clips.twitch.tv/embed?clip=ClipID&...
        video_id = None
        url = None
        if 'clips.twitch.tv/embed?clip=' in embed_url:
            clip_id = embed_url.split('clip=')[1].split('&')[0]
            video_id = clip_id
            # Convert to regular Twitch clip URL
            url = f"https://clips.twitch.tv/{clip_id}"
        else:
            url = embed_url

        return {
            'title': title or 'Highlight',
            'url': url,
            'embed_url': embed_url,
            'thumbnail': thumbnail,
            'video_id': video_id,  # Twitch clip ID
            'duration': None,  # Twitch doesn't provide duration in data attributes
            'platform': 'twitch',
            'view_count': int(view_count) if view_count else None,
            'highlight_id': highlight_id
        }
