from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://www.hltv.org/events/8042/starladder-budapest-major-2025"

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
}

response = requests.get(
    url,
    headers=headers,
    impersonate="chrome110",
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"URL: {response.url}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for stats tables
    tables = soup.find_all('table')
    print(f"\nFound {len(tables)} tables")
    
    for i, table in enumerate(tables):
        print(f"\nTable {i+1}:")
        print(table.get('class'))
        rows = table.find_all('tr')
        if rows:
            print(f"  {len(rows)} rows")
            if len(rows) > 0:
                print(f"  First row: {rows[0].text[:100]}")
