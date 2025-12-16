"""
Debug script to extract highlight video data
"""
import sys
from scrapers.event_highlights import EventHighlightsScraper

scraper = EventHighlightsScraper()
url = f"{scraper.base_url}/events/8042/starladder-budapest-major-2025"
soup = scraper.fetch(url)

if not soup:
    print("Failed to fetch page")
    sys.exit(1)

# Find event-highlights section
highlights_section = soup.find('div', class_='event-highlights')

if not highlights_section:
    print("No highlights section found")
    sys.exit(1)

print(f"✅ Found highlights section")

# Find all highlight-video divs
highlight_videos = highlights_section.find_all('div', class_='highlight-video')
print(f"\n📺 Found {len(highlight_videos)} highlight-video divs\n")

# Inspect first few to understand structure
for i, video in enumerate(highlight_videos[:5]):
    print(f"--- Video {i+1} ---")
    print(f"Classes: {video.get('class')}")

    # Look for data attributes
    for attr in video.attrs:
        if 'data-' in attr or 'id' in attr:
            print(f"  {attr}: {video.get(attr)}")

    # Look for nested elements
    thumbnail = video.find('img', class_='highlights-thumbnail')
    if thumbnail:
        print(f"  Thumbnail src: {thumbnail.get('src')}")
        print(f"  Thumbnail alt: {thumbnail.get('alt')}")

    # Look for links
    link = video.find('a')
    if link:
        print(f"  Link href: {link.get('href')}")
        print(f"  Link text: {link.text.strip() if link.text else 'No text'}")

    # Look for title
    title_elem = video.find('div', class_='highlight-description')
    if title_elem:
        print(f"  Title: {title_elem.text.strip()}")

    # Look for any text content
    text_divs = video.find_all('div', class_=lambda x: x and 'text' in str(x).lower())
    if text_divs:
        print(f"  Text divs: {len(text_divs)}")
        for div in text_divs[:2]:
            print(f"    - {div.get('class')}: {div.text.strip()[:50]}")

    print()

# Check if videos are in different containers
print("\n" + "="*60)
print("CHECKING HIGHLIGHT CONTAINERS")
print("="*60 + "\n")

containers = highlights_section.find_all('div', class_='highlight-video-container')
print(f"Found {len(containers)} video containers\n")

if containers:
    for i, container in enumerate(containers[:3]):
        videos_in_container = container.find_all('div', class_='highlight-video')
        print(f"Container {i+1}: {len(videos_in_container)} videos")
