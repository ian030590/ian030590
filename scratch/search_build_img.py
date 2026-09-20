with open('build_static_articles.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'image' in line.lower() or 'article-featured-img' in line.lower():
        print(f"{i+1}: {line.strip()}")
