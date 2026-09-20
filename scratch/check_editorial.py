import re

with open('article_editorial_copy.py', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.findall(r'unsplash\.com[^\s\'"]+', c)
print(f"Found {len(m)} matches in article_editorial_copy.py")
for item in m[:5]:
    print(" ", item)
