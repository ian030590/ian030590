import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('js/articles-data.js', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'window\.__STATIC_ARTICLES__\s*=\s*(\[.*?\]);', c, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    print(f"Total articles in articles-data.js: {len(data)}")
    img_urls = [art.get('imageUrl') for art in data]
    unique_imgs = set(img_urls)
    print(f"Unique imageUrls: {len(unique_imgs)} / {len(data)}")

    banned = ['photo-1581594693702-fbdc51b2763b', 'photo-1516307365426-bea591f05011']
    found_banned = [b for b in banned if any(b in u for u in img_urls if u)]
    if found_banned:
        print(f"WARNING: Found banned old photos: {found_banned}")
    else:
        print("VERIFIED: No banned old photos in articles-data.js!")

    print("\n--- Key Articles Check ---")
    for art in data:
        if art['id'] in ['VisualRehab_024', 'CognitRehab_007', 'MotorRehab_006', 'MotorRehab_014', 'MotorRehab_015']:
            print(f"[{art['id']}] {art['title']}")
            print(f"  Image: {art['imageUrl']}")
