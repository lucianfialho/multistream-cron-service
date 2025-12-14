"""
Base scraper class using curl_cffi to bypass Cloudflare
"""
from curl_cffi import requests
from bs4 import BeautifulSoup
from typing import Optional
import time
import sys


class BaseScraper:
    """Base class for HLTV scrapers using curl_cffi"""

    def __init__(self):
        self.base_url = "https://www.hltv.org"

    def fetch(self, url: str, retry: int = 3, delay: float = 2.0) -> Optional[BeautifulSoup]:
        """
        Fetch URL with curl_cffi and return BeautifulSoup

        Args:
            url: URL to fetch
            retry: Number of retry attempts
            delay: Base delay for exponential backoff

        Returns:
            BeautifulSoup object or None if failed
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }

        for attempt in range(retry):
            try:
                print(f"Fetching: {url} (attempt {attempt + 1}/{retry})", file=sys.stderr)

                if attempt > 0:
                    wait_time = delay * (2 ** attempt)
                    print(f"⏳ Waiting {wait_time}s...", file=sys.stderr)
                    time.sleep(wait_time)

                response = requests.get(
                    url,
                    headers=headers,
                    impersonate="chrome110",
                    timeout=30,
                    allow_redirects=True
                )

                if response.status_code == 200:
                    print(f"✅ Success: {url}", file=sys.stderr)
                    return BeautifulSoup(response.text, 'html.parser')

                print(f"❌ HTTP {response.status_code}: {url}", file=sys.stderr)

            except Exception as e:
                print(f"❌ Error: {e}", file=sys.stderr)
                if attempt == retry - 1:
                    raise

        return None
