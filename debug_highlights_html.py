"""
Debug script to inspect HTML structure of HLTV event page
"""
import sys
from scrapers.event_highlights import EventHighlightsScraper

scraper = EventHighlightsScraper()
url = f"{scraper.base_url}/events/8042/starladder-budapest-major-2025"
soup = scraper.fetch(url)

if not soup:
    print("Failed to fetch page")
    sys.exit(1)

# Look for anything related to "highlight"
print("\n" + "="*60)
print("SEARCHING FOR HIGHLIGHT-RELATED ELEMENTS")
print("="*60 + "\n")

# Search for any div/section with "highlight" in class
highlight_divs = soup.find_all('div', class_=lambda x: x and 'highlight' in x.lower())
print(f"Found {len(highlight_divs)} divs with 'highlight' in class name:")
for div in highlight_divs:
    print(f"  - {div.get('class')}")

# Search for any element with "highlight" in class
all_highlights = soup.find_all(class_=lambda x: x and 'highlight' in str(x).lower())
print(f"\nFound {len(all_highlights)} total elements with 'highlight' in class:")
for elem in all_highlights[:10]:  # Show first 10
    print(f"  - <{elem.name}> class={elem.get('class')}")

# Search for video/media related elements
print("\n" + "="*60)
print("SEARCHING FOR VIDEO/MEDIA ELEMENTS")
print("="*60 + "\n")

iframes = soup.find_all('iframe')
print(f"Found {len(iframes)} iframes:")
for iframe in iframes:
    print(f"  - src: {iframe.get('src')}")

videos = soup.find_all('video')
print(f"\nFound {len(videos)} video elements")

# Search for YouTube links
youtube_links = soup.find_all('a', href=lambda x: x and ('youtube.com' in x or 'youtu.be' in x))
print(f"\nFound {len(youtube_links)} YouTube links:")
for link in youtube_links[:5]:
    print(f"  - {link.get('href')}")
    if link.text.strip():
        print(f"    Text: {link.text.strip()}")

# Look for sections that might contain videos
print("\n" + "="*60)
print("PAGE SECTIONS")
print("="*60 + "\n")

main_sections = soup.find_all(['section', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['event', 'video', 'media', 'content']))
print(f"Found {len(main_sections)} main sections:")
for section in main_sections[:15]:
    classes = section.get('class', [])
    print(f"  - <{section.name}> class={classes}")
