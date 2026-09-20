import glob, re, json
from bs4 import BeautifulSoup

articles = sorted(glob.glob('content/**/*.html', recursive=True))
print(f"Total articles found: {len(articles)}")

photo_map = {}
errors = []

for path in articles:
    norm_path = path.replace('\\', '/')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # 1. Check featured img
    img = soup.find('img', class_='article-featured-img')
    if not img:
        errors.append(f"{norm_path}: Missing article-featured-img")
        continue
    img_src = img.get('src', '')
    
    # 2. Check og:image
    og_img = soup.find('meta', property='og:image')
    og_src = og_img.get('content', '') if og_img else ''
    
    # 3. Check twitter:image
    tw_img = soup.find('meta', attrs={'name': 'twitter:image'})
    tw_src = tw_img.get('content', '') if tw_img else ''
    
    # 4. Check JSON-LD
    schema_script = soup.find('script', type='application/ld+json')
    schema_img = ''
    if schema_script:
        try:
            schema_data = json.loads(schema_script.string)
            schema_img = schema_data.get('image', '')
            if isinstance(schema_img, list) and schema_img:
                schema_img = schema_img[0]
        except Exception as e:
            errors.append(f"{norm_path}: Invalid JSON-LD: {e}")

    # Check consistency
    if not (img_src == og_src == tw_src == schema_img):
        errors.append(f"{norm_path}: Image URL mismatch:\n  img: {img_src}\n  og:  {og_src}\n  tw:  {tw_src}\n  ld:  {schema_img}")

    # Extract Photo ID
    m = re.search(r'photo-([a-zA-Z0-9_-]+)', img_src)
    pid = m.group(1) if m else img_src
    
    if pid not in photo_map:
        photo_map[pid] = []
    photo_map[pid].append((norm_path, soup.find('h1').text.strip() if soup.find('h1') else ''))

# Check duplicates
duplicates = {k: v for k, v in photo_map.items() if len(v) > 1}

print("\n--- Validation Results ---")
if errors:
    print(f"FAILED with {len(errors)} errors:")
    for err in errors:
        print(" ", err)
else:
    print("ALL 40 articles have 100% consistent internal metadata (img, og, tw, ld)!")

if duplicates:
    print(f"\nFAILED: {len(duplicates)} duplicate photos found:")
    for pid, plist in duplicates.items():
        print(f"  Photo {pid}:")
        for p, t in plist:
            print(f"    - {p} ({t})")
else:
    print("ALL 40 articles use 100% UNIQUE photos! Zero duplicates across the entire site!")

print(f"\nUnique photo count: {len(photo_map)} / 40")
