import urllib.request
import re

url = 'https://information-literacy.blogspot.com/2021/01/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        for m in set(re.findall(r'https?://[^\s\"\'<>]*(?:unsplash|photo)[^\s\"\'<>]*', content)):
            print(m)
except Exception as e:
    print(e)
