"""
Test script to scrape highlights from Budapest Major
"""
import sys
from scrapers.event_highlights import EventHighlightsScraper

# Test with Budapest Major
scraper = EventHighlightsScraper()
highlights = scraper.scrape("8042")

print(f"\n{'='*60}")
print(f"HIGHLIGHTS FOUND: {len(highlights)}")
print(f"{'='*60}\n")

for i, h in enumerate(highlights, 1):
    print(f"{i}. {h.get('title', 'No title')}")
    print(f"   URL: {h.get('url')}")
    print(f"   Platform: {h.get('platform')}")
    if h.get('video_id'):
        print(f"   Video ID: {h.get('video_id')}")
    if h.get('duration'):
        print(f"   Duration: {h.get('duration')}")
    print()
