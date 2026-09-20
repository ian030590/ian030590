with open('build_static_articles.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'ADDITIONAL_CONTENT_FOLDERS' in line:
            print(f"{i+1}: {line.strip()}")
