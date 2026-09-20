import urllib.request
import urllib.parse
import re
import json

def search_ddg_unsplash(term):
    query = f'site:images.unsplash.com "{term}"'
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Extract photo URLs
            links = re.findall(r'https?://images\.unsplash\.com/(photo-[a-zA-Z0-9_-]+)', html)
            return list(dict.fromkeys(links))
    except Exception as e:
        print(f"Error searching for {term}: {e}")
        return []

if __name__ == '__main__':
    for q in ["caregiver elderly", "wheelchair", "physiotherapy", "clock face", "eye chart"]:
        res = search_ddg_unsplash(q)
        print(f"Query '{q}': {len(res)} results -> {res[:3]}")
