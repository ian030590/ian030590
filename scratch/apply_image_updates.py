import re, glob
from bs4 import BeautifulSoup

replacements = {
    'content/VisualRehab/024_視覺復健_光學放大輔具處方與使用訓練.html': (
        'https://images.unsplash.com/photo-1762180980045-4d7c5a6c0fc9?auto=format&fit=crop&w=1200&h=800&q=80',
        '木質書桌檯燈旁的手持光學放大鏡，呈現低視能閱讀與精細輔具處方評估。圖片來源：Unsplash。'
    ),
    'content/CognitRehab/007_認知復健_中風後心理健康.html': (
        'https://images.unsplash.com/photo-1555697752-da25a4b1025b?auto=format&fit=crop&w=1200&h=800&q=80',
        '長者於床上安詳沉睡休息，呈現中風後大腦器質性神經疲勞、情緒與睡眠障礙之鑑別診斷。圖片來源：Unsplash。'
    ),
    'content/MotorRehab/006_動作復健_偏癱肩痛與半脫位.html': (
        'https://images.unsplash.com/photo-1668422550551-972d12892971?auto=format&fit=crop&w=1200&h=800&q=80',
        '治療師雙手承托並進行肩關節與患側肢體徒手復健伸展，呈現中風後肩痛與肩關節半脫位之臨床處置。圖片來源：Unsplash。'
    ),
    'content/MotorRehab/014_動作復健_輔具矯具與輪椅.html': (
        'https://images.unsplash.com/photo-1685657814797-83706c4e5279?auto=format&fit=crop&w=1200&h=800&q=80',
        '病房床邊長者乘坐專業復健輪椅，呈現中風與行動障礙個案之輪椅擺位與行動輔具適配。圖片來源：Unsplash。'
    ),
    'content/MotorRehab/015_動作復健_吞嚥與營養.html': (
        'https://images.unsplash.com/photo-1757489345059-31d51e241a3e?auto=format&fit=crop&w=1200&h=800&q=80',
        '質地均質滑順的糊狀濃湯與湯匙，呈現中風吞嚥障礙之飲食質地調整與安全進食照護。圖片來源：Unsplash。'
    ),
    'content/VisualRehab/003_視覺復健_低視能評估與目標.html': (
        'https://images.unsplash.com/photo-1705357311681-17449eb278d1?auto=format&fit=crop&w=1200&h=800&q=80',
        '臨床視力檢查燈箱與字母視標，呈現低視能評估中視力敏銳度與對比度之全面檢查。圖片來源：Unsplash。'
    ),
    'content/VisualRehab/007_視覺復健_微視野與偏心注視.html': (
        'https://images.unsplash.com/photo-1483519173755-be893fab1f46?auto=format&fit=crop&w=1200&h=800&q=80',
        '人類眼睛瞳孔與虹膜微距特寫，呈現黃斑部病變中心暗點與偏心注視訓練之視覺機制。圖片來源：Unsplash。'
    ),
    'content/VisualRehab/027_視覺復健_居家環境改造與日常自理EPIC架構.html': (
        'https://images.unsplash.com/photo-1556911220-dabc1f02913a?auto=format&fit=crop&w=1200&h=800&q=80',
        '明亮高對比的廚房料理檯面與備料砧板，呈現低視能居家環境改造與安全烹飪訓練。圖片來源：Unsplash。'
    ),
    'content/VisualRehab/029_視覺復健_時鐘面定位法評估中心暗點與偏心注視.html': (
        'https://images.unsplash.com/photo-1643424975787-f134e78ecbc8?auto=format&fit=crop&w=1200&h=800&q=80',
        '指針指向不同方位的時鐘錶面，呈現偏心注視時鐘面定位法之方位引導概念。圖片來源：Unsplash。'
    ),
    'content/CognitRehab/002_認知復健_科技支持認知訓練.html': (
        'https://images.unsplash.com/photo-1666886573301-b5d526cfd518?auto=format&fit=crop&w=1200&h=800&q=80',
        '醫療工作者使用平板電腦操作數位應用程式，呈現認知訓練軟體之臨床應用與生活轉化。圖片來源：Unsplash。'
    ),
    'content/CognitRehab/004_認知復健_失語症與支持性溝通.html': (
        'https://images.unsplash.com/photo-1758691461935-202e2ef6b69f?auto=format&fit=crop&w=1200&h=800&q=80',
        '醫療人員專注傾聽並與個案面對面深度溝通，呈現中風後失語症之溝通支持與自主決策。圖片來源：Unsplash。'
    ),
    'content/MotorRehab/013_動作復健_上肢與日常活動.html': (
        'https://images.unsplash.com/photo-1730382624360-9cf5609c8364?auto=format&fit=crop&w=1200&h=800&q=80',
        '手部前三指精細捏取木質積木進行抓握與堆疊，呈現中風患側手動作復健與任務導向訓練。圖片來源：Unsplash。'
    ),
    'content/MotorRehab/008_動作復健_中風跌倒與骨骼健康.html': (
        'https://images.unsplash.com/photo-1633158832532-f71e9c7ac6d6?auto=format&fit=crop&w=1200&h=800&q=80',
        '雙手穩固握持前臂支撐手杖輔助站立與步行，呈現中風步態平衡訓練與跌倒預防防護。圖片來源：Unsplash。'
    ),
    'content/MotorRehab/002_動作復健_急性期動員.html': (
        'https://images.unsplash.com/photo-1646082275130-347d10885c5f?auto=format&fit=crop&w=1200&h=800&q=80',
        '住院病患於病房中坐於輪椅準備進行活動，呈現急性中風早期動員之漸進式下床時機與劑量。圖片來源：Unsplash。'
    ),
    'content/CognitRehab/009_認知復健_照護者與遠距轉銜.html': (
        'https://images.unsplash.com/photo-1584515933487-779824d29309?auto=format&fit=crop&w=1200&h=800&q=80',
        '病患與家屬雙手緊密交握支持，呈現中風出院返家後照護者陪伴與居家社區復健銜接。圖片來源：Unsplash。'
    ),
    'content/VisualRehab/026_視覺復健_閱讀與書寫功能重建技巧.html': (
        'https://images.unsplash.com/photo-1628578823562-aad3908f4f88?auto=format&fit=crop&w=1200&h=800&q=80',
        '讀者在明亮閱讀燈光下翻閱書本文字，呈現低視能點讀、長文連讀與書寫視覺功能重建。圖片來源：Unsplash。'
    ),
    'content/MotorRehab/003_動作復健_皮膚與攣縮預防.html': (
        'https://images.unsplash.com/photo-1545463913-5083aa7359a6?auto=format&fit=crop&w=1200&h=800&q=80',
        '治療師細心觸診與伸展患者緊繃足踝關節，呈現中風後痙攣、關節攣縮與肢體皮膚評估照護。圖片來源：Unsplash。'
    ),
    'content/VisualRehab/013_視覺復健_跌倒與定向行動.html': (
        'https://images.unsplash.com/photo-1785400822205-2cfe8039326d?auto=format&fit=crop&w=1200&h=800&q=80',
        '地鐵通道明亮黃色無障礙導盲磚動線，呈現低視能跌倒防範、定向行動與安全環境導引。圖片來源：Unsplash。'
    ),
    'content/VisualRehab/016_視覺復健_心理調適與夏爾博內.html': (
        'https://images.unsplash.com/photo-1772464346751-788b0745ec93?auto=format&fit=crop&w=1200&h=800&q=80',
        '銀髮長者於室內凝望窗外光影，呈現視力顯著減退後的心理適應、夏爾博內症候群視幻覺與情緒支持。圖片來源：Unsplash。'
    ),
    'content/VisualRehab/025_視覺復健_電子擴視科技與智慧輔助無障礙.html': (
        'https://images.unsplash.com/photo-1676107779594-7a23bd99e07c?auto=format&fit=crop&w=1200&h=800&q=80',
        '雙手捧持高對比電子顯示螢幕閱讀文字，呈現電子擴視科技、螢幕報讀與數位視覺無障礙。圖片來源：Unsplash。'
    ),
    'content/VisualRehab/001_視覺復健_視覺復健照護連續體.html': (
        'https://images.unsplash.com/photo-1766310549795-dd0fc75d499f?auto=format&fit=crop&w=1200&h=800&q=80',
        '眼科專業裂隙燈儀器檢查，呈現眼科醫療處置與低視能視覺復健之照護連續體協同模式。圖片來源：Unsplash。'
    )
}

def update_article_image(filepath, new_url, new_caption):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Find the old image URL in the article
    m = re.search(r'<img[^>]+class="article-featured-img"[^>]+src="([^"]+)"', html)
    if not m:
        # try another order of attributes
        m = re.search(r'<img[^>]+src="([^"]+)"[^>]+class="article-featured-img"', html)
    if not m:
        print(f"FAILED TO FIND FEATURED IMG IN {filepath}")
        return False

    old_url = m.group(1)
    print(f"Updating {filepath}:")
    print(f"  Old URL: {old_url}")
    print(f"  New URL: {new_url}")

    # 1. Replace og:image
    html = re.sub(
        r'(<meta\s+property="og:image"\s+content=")[^"]+(")',
        rf'\g<1>{new_url}\g<2>',
        html
    )

    # 2. Replace twitter:image
    html = re.sub(
        r'(<meta\s+name="twitter:image"\s+content=")[^"]+(")',
        rf'\g<1>{new_url}\g<2>',
        html
    )

    # 3. Replace schema JSON-LD "image"
    # Matches "image": "..." or "image": ["..."]
    html = re.sub(
        r'("image":\s*)"[^"]+"',
        rf'\g<1>"{new_url}"',
        html
    )
    html = re.sub(
        r'("image":\s*\[\s*)"[^"]+"(\s*\])',
        rf'\g<1>"{new_url}"\g<2>',
        html
    )

    # 4. Replace img src and alt
    # Extract plain alt without "圖片來源：Unsplash。" for alt attribute
    clean_alt = re.sub(r'圖片來源.*$', '', new_caption).strip()
    html = re.sub(
        r'(<img\s+src=")[^"]+("\s+alt=")[^"]+("\s+class="article-featured-img")',
        rf'\g<1>{new_url}\g<2>{clean_alt}\g<3>',
        html
    )
    # Alternative ordering of attributes
    html = re.sub(
        r'(<img\s+class="article-featured-img"\s+src=")[^"]+("\s+alt=")[^"]+(")',
        rf'\g<1>{new_url}\g<2>{clean_alt}\g<3>',
        html
    )

    # 5. Replace figcaption content
    html = re.sub(
        r'(<figcaption\s+class="article-figcaption">)[^<]+(</figcaption>)',
        rf'\g<1>{new_caption}\g<2>',
        html
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return True

success_count = 0
for path, (url, cap) in replacements.items():
    norm_path = path.replace('/', '\\')
    if update_article_image(norm_path, url, cap):
        success_count += 1

print(f"\nSuccessfully updated {success_count} / {len(replacements)} articles!")
