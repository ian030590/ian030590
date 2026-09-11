import os
import sys
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r'P:\3_WebSite\ian030590')
CONTENT_DIR = BASE_DIR / 'content'
CSS_FILE = BASE_DIR / 'css' / 'style.css'
SITEMAP_FILE = BASE_DIR / 'sitemap.xml'
ARTICLES_DATA_FILE = BASE_DIR / 'js' / 'articles-data.js'
BLOG_HTML_FILE = BASE_DIR / 'blog.html'
MAIN_JS_FILE = BASE_DIR / 'js' / 'main.js'

SITE_BASE_URL = 'https://ian030590.github.io'

# 1. DigitalLearning File Mapping: (old_filename, new_filename, short_topic, cluster, order)
DL_MAPPING = {
    '00_Blogger_Series_Introduction.html': (
        '001_AI產品架構思維系列總覽_非工程師的12講導讀總綱.html',
        '系列總覽',
        '非工程師的「AI 產品架構思維」12 講專題',
        1,
        '導讀總綱'
    ),
    'Post_01_AI_Mental_Model.html': (
        '002_心智模型_破除全能迷思用聘請頂尖實習生的心態理解大型語言模型.html',
        '心智模型',
        '非工程師的「AI 產品架構思維」12 講專題',
        2,
        '基礎認知與軟體架構'
    ),
    'Post_02_Software_Architecture_Lego.html': (
        '003_軟體骨架_非工程師的軟體樂高課前端後端API與資料庫到底在幹嘛.html',
        '軟體骨架',
        '非工程師的「AI 產品架構思維」12 講專題',
        3,
        '基礎認知與軟體架構'
    ),
    'Post_03_Prompt_Engineering_Secret.html': (
        '004_提示工程_別再盲目摸索提示詞寫出工業級Prompt的標準作業程序.html',
        '提示工程',
        '非工程師的「AI 產品架構思維」12 講專題',
        4,
        '提示工程與知識檢索'
    ),
    'Post_04_RAG_External_Brain.html': (
        '005_知識外掛_終結AI瞎掰RAG檢索增強生成如何打造專屬外掛大腦.html',
        '知識外掛',
        '非工程師的「AI 產品架構思維」12 講專題',
        5,
        '提示工程與知識檢索'
    ),
    'Post_05_AI_Agents_Action.html': (
        '006_智慧體行動_會思考還會動手自主AI智慧體是得力助手還是碎鈔機.html',
        '智慧體行動',
        '非工程師的「AI 產品架構思維」12 講專題',
        6,
        '自主智慧體與多Agent協同'
    ),
    'Post_06_Multi_Agent_and_MCP.html': (
        '007_協同協定_一人開一間虛擬公司多智慧體協同與AI界TypeC接口MCP.html',
        '協同協定',
        '非工程師的「AI 產品架構思維」12 講專題',
        7,
        '自主智慧體與多Agent協同'
    ),
    'Post_07_Vibe_Coding_Trap.html': (
        '008_防翻車指南_隨興編程是效率革命還是維運災難不懂代碼如何用AI開發工具不翻車.html',
        '防翻車指南',
        '非工程師的「AI 產品架構思維」12 講專題',
        8,
        '工程防護與資訊安全'
    ),
    'Post_08_LLM_Cybersecurity.html': (
        '009_資訊安全_AI時代的駭客江湖一句話就能套出公司機密的提示詞注入攻擊.html',
        '資訊安全',
        '非工程師的「AI 產品架構思維」12 講專題',
        9,
        '工程防護與資訊安全'
    ),
    'Post_09_Guardrails_and_Safety.html': (
        '010_安全護欄_給AI戴上安全韁繩如何打造不說髒話不洩漏個資的防護欄.html',
        '安全護欄',
        '非工程師的「AI 產品架構思維」12 講專題',
        10,
        '工程防護與資訊安全'
    ),
    'Post_10_Evaluating_AI.html': (
        '011_量化評測_你的AI到底有多聰明別再看感覺讓AI當裁判的科學評測法.html',
        '量化評測',
        '非工程師的「AI 產品架構思維」12 講專題',
        11,
        '評測成本與長期維運'
    ),
    'Post_11_Cost_and_Latency.html': (
        '012_成本與延遲_每聊一句都在燒錢破解AI產品的負毛利陷阱與延遲控制.html',
        '成本與延遲',
        '非工程師的「AI 產品架構思維」12 講專題',
        12,
        '評測成本與長期維運'
    ),
    'Post_12_AI_Lifecycle_and_Operations.html': (
        '013_生命週期運維_發布不是結束AI產品上線後如何不生病不擺爛的長照指南.html',
        '生命週期運維',
        '非工程師的「AI 產品架構思維」12 講專題',
        13,
        '評測成本與長期維運'
    ),
}

# 2. Add Article CSS to style.css if not present
ARTICLE_CSS = """
/* ==========================================================================
   Article Detail & Reading Experience System (EEAT & Topic Clusters)
   ========================================================================== */

.article-page-layout {
  padding-top: 32px;
  padding-bottom: 80px;
}

.breadcrumb-trail {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 28px;
  font-size: 14px;
  color: var(--muted);
}

.breadcrumb-trail a {
  color: var(--muted);
  text-decoration: none;
  transition: color 0.15s ease;
}

.breadcrumb-trail a:hover {
  color: var(--primary);
}

.breadcrumb-separator {
  color: var(--color-border-strong);
  font-size: 12px;
  user-select: none;
}

.breadcrumb-current {
  color: var(--ink);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 320px;
}

.article-container {
  max-width: 880px;
  margin: 0 auto;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 44px 40px 36px 40px;
  box-shadow: var(--shadow);
}

@media (max-width: 768px) {
  .article-container {
    padding: 24px 18px 24px 18px;
    border-radius: 10px;
  }
  .breadcrumb-current {
    max-width: 180px;
  }
}

.article-detail-header {
  margin-bottom: 32px;
  border-bottom: 1px solid var(--line);
  padding-bottom: 24px;
}

.article-tag-badges {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.article-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--accent-soft);
  color: var(--color-badge-text);
  font-size: 13.5px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  letter-spacing: 0.02em;
}

.article-badge.cluster-badge {
  background: var(--color-bg-surface-subtle);
  color: var(--muted);
  border: 1px solid var(--line);
}

.article-title {
  font-size: 32px;
  line-height: 1.35;
  color: var(--ink);
  margin: 0 0 16px 0;
  font-weight: 800;
  letter-spacing: -0.01em;
}

@media (max-width: 768px) {
  .article-title {
    font-size: 24px;
  }
}

.article-meta-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 14px;
  color: var(--muted);
}

.article-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.article-meta-item .material-symbols-outlined {
  font-size: 16px;
}

.article-featured-figure {
  margin: 0 0 32px 0;
  text-align: center;
}

.article-featured-img {
  width: 100%;
  max-height: 480px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
}

.article-figcaption {
  font-size: 13.5px;
  color: var(--muted);
  margin-top: 10px;
  line-height: 1.6;
  text-align: center;
}

.article-lead-box {
  background-color: var(--surface-soft);
  border: 1px solid var(--line);
  border-left: 5px solid var(--primary);
  padding: 22px 26px;
  margin-bottom: 36px;
  border-radius: 0 10px 10px 0;
}

.article-lead-box-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--primary-strong);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.article-lead-box p {
  margin: 0;
  font-size: 17px;
  line-height: 1.85;
  color: var(--ink);
  font-weight: 500;
}

.article-lead-box ul {
  margin: 0;
  padding-left: 20px;
  font-size: 16.5px;
  line-height: 1.8;
  color: var(--ink);
}

.article-body-content {
  font-size: 18px;
  line-height: 1.85;
  color: var(--ink);
}

.article-body-content p {
  margin: 0 0 22px 0;
  line-height: 1.85;
}

.article-body-content h2 {
  font-size: 24px;
  line-height: 1.4;
  color: var(--ink);
  border-left: 5px solid var(--primary);
  padding-left: 14px;
  margin-top: 48px;
  margin-bottom: 20px;
  font-weight: 800;
}

.article-body-content h3 {
  font-size: 20px;
  line-height: 1.4;
  color: var(--ink);
  margin-top: 32px;
  margin-bottom: 14px;
  font-weight: 700;
}

.article-body-content ul,
.article-body-content ol {
  margin: 0 0 24px 0;
  padding-left: 26px;
  line-height: 1.8;
}

.article-body-content li {
  margin-bottom: 10px;
}

.article-body-content strong {
  color: var(--ink);
}

/* Callout blocks inside body */
.callout-box {
  background: var(--surface-soft);
  border: 1px solid var(--line);
  border-left: 5px solid var(--primary);
  border-radius: 0 8px 8px 0;
  padding: 20px 24px;
  margin: 28px 0;
}

.callout-box.warning {
  border-left-color: #e53e3e;
  background: rgba(229, 62, 62, 0.06);
}

.callout-box.amber {
  border-left-color: #dd6b20;
  background: rgba(221, 107, 32, 0.06);
}

.callout-box.success {
  border-left-color: #137333;
  background: rgba(19, 115, 51, 0.06);
}

.table-wrapper {
  overflow-x: auto;
  margin: 28px 0;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.article-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 15.5px;
  background: var(--surface);
}

.article-table th {
  background: var(--surface-soft);
  color: var(--ink);
  padding: 13px 16px;
  font-weight: 700;
  border-bottom: 2px solid var(--line);
}

.article-table td {
  padding: 13px 16px;
  border-bottom: 1px solid var(--line);
  color: var(--ink);
}

.code-terminal-block {
  background: var(--slate-950);
  color: var(--slate-50);
  padding: 18px 20px;
  border-radius: 8px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 15px;
  line-height: 1.65;
  margin: 28px 0;
  overflow-x: auto;
  border: 1px solid var(--line);
}

/* References */
.article-references {
  margin-top: 48px;
  border-top: 2px solid var(--line);
  padding-top: 28px;
}

.article-references h2 {
  font-size: 20px;
  color: var(--ink);
  margin-bottom: 18px;
  border-left: 5px solid var(--muted);
  padding-left: 12px;
}

.article-references ol {
  font-size: 15px;
  line-height: 1.75;
  color: var(--muted);
  padding-left: 24px;
  margin: 0;
}

.article-references li {
  margin-bottom: 14px;
}

.article-references a {
  color: var(--primary);
  text-decoration: underline;
  word-break: break-all;
}

/* Author EEAT Card */
.author-eeat-card {
  margin-top: 48px;
  background: var(--surface-soft);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 28px 30px;
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

@media (max-width: 640px) {
  .author-eeat-card {
    flex-direction: column;
    padding: 20px;
  }
}

.author-avatar-wrap {
  flex-shrink: 0;
}

.author-avatar-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--accent-soft);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  border: 2px solid var(--line);
}

.author-eeat-info {
  flex: 1;
}

.author-eeat-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.author-credential-badge {
  font-size: 12px;
  background: var(--accent-soft);
  color: var(--color-badge-text);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.author-eeat-title {
  font-size: 14px;
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 12px;
}

.author-eeat-bio {
  font-size: 14.5px;
  color: var(--muted);
  line-height: 1.65;
  margin-bottom: 14px;
}

.author-eeat-statement {
  font-size: 13px;
  color: var(--muted);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px 14px;
  margin-bottom: 16px;
  line-height: 1.6;
}

.author-eeat-links {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.author-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
  text-decoration: none;
  background: var(--surface);
  border: 1px solid var(--line);
  padding: 5px 12px;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.author-link-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

/* Topic Cluster / Series Navigation */
.topic-cluster-nav {
  margin-top: 40px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}

.topic-cluster-header {
  background: var(--surface-soft);
  padding: 16px 22px;
  border-bottom: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-cluster-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--ink);
  display: flex;
  align-items: center;
  gap: 8px;
}

.topic-cluster-progress {
  font-size: 13px;
  color: var(--muted);
  font-weight: 600;
}

.topic-cluster-list {
  list-style: none;
  margin: 0;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 380px;
  overflow-y: auto;
}

.topic-cluster-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14.5px;
  text-decoration: none;
  color: var(--muted);
  transition: all 0.15s ease;
}

.topic-cluster-item:hover {
  background: var(--surface-soft);
  color: var(--primary);
}

.topic-cluster-item.active {
  background: var(--accent-soft);
  color: var(--color-badge-text);
  font-weight: 700;
}

.topic-cluster-item-num {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-weight: 700;
  font-size: 13px;
  opacity: 0.8;
}

.topic-cluster-item-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.topic-cluster-item-current {
  font-size: 11px;
  background: var(--primary);
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Prev Next Navigation */
.prev-next-nav {
  margin-top: 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 600px) {
  .prev-next-nav {
    grid-template-columns: 1fr;
  }
}

.prev-next-card {
  display: flex;
  flex-direction: column;
  padding: 16px 18px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  text-decoration: none;
  color: var(--ink);
  transition: all 0.2s ease;
}

.prev-next-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.prev-next-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.prev-next-title {
  font-size: 14.5px;
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-bottom-actions {
  margin-top: 36px;
  text-align: center;
}
"""

def update_css():
    css_content = CSS_FILE.read_text(encoding='utf-8')
    if 'Article Detail & Reading Experience System' not in css_content:
        print('Appending article CSS to style.css...')
        CSS_FILE.write_text(css_content + '\n' + ARTICLE_CSS, encoding='utf-8')
    else:
        print('Article CSS already exists in style.css.')

def clean_inner_body(soup_body):
    """Clean up inline styles from body elements to make them adapt to light/dark themes."""
    # Convert tables
    for table in soup_body.find_all('table'):
        table['class'] = ['article-table']
        table.attrs.pop('style', None)
        # Wrap table in table-wrapper if not already wrapped
        if not table.parent or 'table-wrapper' not in table.parent.get('class', []):
            wrapper = soup_body.new_tag('div', **{'class': 'table-wrapper'})
            table.wrap(wrapper)
            
    for th in soup_body.find_all('th'):
        th.attrs.pop('style', None)
    for td in soup_body.find_all('td'):
        td.attrs.pop('style', None)
    for tr in soup_body.find_all('tr'):
        tr.attrs.pop('style', None)
        
    # Convert headings
    for h in soup_body.find_all(['h1', 'h2', 'h3', 'h4']):
        h.attrs.pop('style', None)
        
    # Convert paragraphs and lists
    for p in soup_body.find_all('p'):
        p.attrs.pop('style', None)
    for ul in soup_body.find_all(['ul', 'ol', 'li']):
        ul.attrs.pop('style', None)
        
    # Convert callouts
    for div in soup_body.find_all('div'):
        style = div.get('style', '').lower()
        if 'fff5f5' in style or 'e53e3e' in style: # warning
            div['class'] = ['callout-box', 'warning']
            div.attrs.pop('style', None)
        elif 'fffaf0' in style or 'dd6b20' in style: # amber warning
            div['class'] = ['callout-box', 'amber']
            div.attrs.pop('style', None)
        elif 'e6f4ea' in style or '137333' in style or 'ebf8ff' in style: # success / info
            div['class'] = ['callout-box', 'success']
            div.attrs.pop('style', None)
        elif 'eff6ff' in style or 'f8fafc' in style or 'f7fafc' in style:
            div['class'] = ['callout-box']
            div.attrs.pop('style', None)
        elif 'ui-monospace' in style or 'monospace' in style or '#0f172a' in style:
            div['class'] = ['code-terminal-block']
            div.attrs.pop('style', None)
            
    # Clean up spans with hardcoded color
    for span in soup_body.find_all('span'):
        style = span.get('style', '').lower()
        if 'background' in style:
            text = span.get_text().strip()
            if 'cor 1' in text.lower():
                span['class'] = ['article-badge']
            elif 'cor 3' in text.lower():
                span['class'] = ['article-badge', 'badge-danger']
            span.attrs.pop('style', None)
        elif 'color' in style and ('#2d3748' in style or '#1a202c' in style or '#0f172a' in style):
            span.attrs.pop('style', None)
            
    return str(soup_body)

def collect_article_metadata():
    folders = [
        ('DigitalLearning', '數位學習', '科技深度專題', 'digital'),
        ('OccupationalTherapy', '職能治療', '神經復健實證專題', 'ot'),
        ('VisualTherapy', '視覺復健', '低視力復健實證專題', 'vt'),
    ]
    
    all_articles = []
    
    for folder, cat_name, cat_badge, cat_slug in folders:
        folder_path = CONTENT_DIR / folder
        files = sorted(folder_path.glob('*.html'))
        for f in files:
            content = f.read_text(encoding='utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Identify mapping
            if folder == 'DigitalLearning':
                if f.name in DL_MAPPING:
                    new_filename, short_topic, cluster, order, sub_cluster = DL_MAPPING[f.name]
                elif f.name.startswith(('001_', '002_', '003_', '004_', '005_', '006_', '007_', '008_', '009_', '010_', '011_', '012_', '013_')):
                    order = int(f.name[:3])
                    new_filename = f.name
                    short_topic = f.name[4:].replace('.html', '').split('_')[0]
                    cluster = '非工程師的「AI 產品架構思維」12 講專題'
                    sub_cluster = '導讀總綱' if order == 1 else ('基礎認知與軟體架構' if order <= 3 else ('提示工程與知識檢索' if order <= 5 else ('自主智慧體與多Agent協同' if order <= 7 else ('工程防護與資訊安全' if order <= 10 else '評測成本與長期維運'))))
                else:
                    continue
                date_published = f'2026-04-{10 + (order - 1) * 2:02d}T08:00:00+08:00'
            else:
                if f.name[:3].isdigit():
                    order = int(f.name[:3])
                    new_filename = f.name
                    short_topic = f.name[4:].replace('.html', '').split('_')[0]
                else:
                    order = int(f.name[:2])
                    new_filename = f'{order:03d}_{f.name[3:]}'
                    short_topic = f.name[3:].replace('.html', '').split('_')[0]
                    
                if folder == 'OccupationalTherapy':
                    date_published = f'2026-01-{10 + (order - 1) * 2:02d}T08:00:00+08:00' if order <= 10 else f'2026-02-{1 + (order - 11) * 2:02d}T08:00:00+08:00'
                    if order <= 10:
                        cluster = '中風神經復健與全人照護'
                        sub_cluster = '急性期與動作功能重建'
                    else:
                        cluster = '中風後神經視覺復健'
                        sub_cluster = '神經視覺功能重建與代償'
                else: # VisualTherapy
                    date_published = f'2026-02-{15 + (order - 1) * 2:02d}T08:00:00+08:00' if order <= 8 else f'2026-03-{1 + (order - 9) * 2:02d}T08:00:00+08:00'
                    if order <= 9:
                        cluster = '低視力臨床評估與光學處方科學'
                        sub_cluster = '功能評估與輔具處方'
                    elif order <= 14:
                        cluster = '環境人因工程、安全自理與防跌防護'
                        sub_cluster = '環境改造與居家自理'
                    else:
                        cluster = '特殊病徵、心理調適與跨專業協同'
                        sub_cluster = '跨專業全人照護'

            # 1. Title
            h1 = soup.find('h1')
            title = h1.get_text().strip() if h1 else ''
            if not title and soup.title:
                title = soup.title.get_text().strip()
                
            # 2. Header Spans / Tags
            header = soup.find('header')
            spans = [s.get_text().strip() for s in header.find_all('span')] if header else []
            
            tags = [cat_name]
            for s in spans:
                cleaned = re.sub(r'^(?:視角|主題)[：:]\s*', '', s).strip()
                if cleaned and cleaned not in tags and '建議閱讀時間' not in cleaned and '科技深度專題' not in cleaned:
                    for part in re.split(r'[,、/|]', cleaned):
                        part = part.strip()
                        if part and len(part) <= 15 and part not in tags:
                            tags.append(part)
            if cluster not in tags:
                tags.append(cluster)
                
            # 3. Read time
            read_time = '約 5 分鐘閱讀'
            for s in spans:
                m = re.search(r'([0-9]+)\s*分鐘', s)
                if m:
                    read_time = f'約 {m.group(1)} 分鐘閱讀'
                    break
                    
            # 4. Image
            fig = soup.find('figure')
            img = fig.find('img') if fig else soup.find('img')
            img_src = img['src'] if img and img.has_attr('src') else ''
            caption = fig.find('figcaption').get_text().strip() if fig and fig.find('figcaption') else ''
            if not caption and img and img.get('alt'):
                caption = img.get('alt')
                
            # 5. Executive Summary
            summary = ''
            header_p = header.find('p') if header else None
            if header_p and len(header_p.get_text().strip()) > 20:
                summary = header_p.get_text().strip()
            else:
                for div in soup.find_all('div'):
                    style = div.get('style', '')
                    if 'border-left' in style and ('f7fafc' in style or 'f8fafc' in style or 'eff6ff' in style):
                        p_in_div = div.find('p')
                        if p_in_div:
                            summary = p_in_div.get_text().strip()
                        else:
                            summary = div.get_text().strip()
                        break
            if not summary:
                first_p = soup.find('p')
                summary = first_p.get_text().strip() if first_p else title
                
            # 6. References
            ref_sec = soup.find(['section', 'footer'], class_=lambda c: c and 'reference' in c) or soup.find('footer')
            citations = []
            if ref_sec:
                for li in ref_sec.find_all('li'):
                    a = li.find('a')
                    cit_text = li.get_text().strip()
                    cit_url = a['href'] if a and a.has_attr('href') else ''
                    citations.append({'text': cit_text, 'url': cit_url})
                    
            # 7. Raw body content
            if folder == 'DigitalLearning':
                news_article = soup.find('div', class_='news-article')
                if news_article:
                    na_copy = BeautifulSoup(str(news_article), 'html.parser')
                    if na_copy.find('header'):
                        na_copy.find('header').decompose()
                    if na_copy.find('figure'):
                        na_copy.find('figure').decompose()
                    if na_copy.find('footer'):
                        na_copy.find('footer').decompose()
                    if na_copy.find('style'):
                        na_copy.find('style').decompose()
                    body_html = str(na_copy)
                else:
                    body_soup = BeautifulSoup(content, 'html.parser')
                    if body_soup.find('header'):
                        body_soup.find('header').decompose()
                    if body_soup.find('figure'):
                        body_soup.find('figure').decompose()
                    if body_soup.find('footer'):
                        body_soup.find('footer').decompose()
                    if body_soup.find('style'):
                        body_soup.find('style').decompose()
                    body_html = str(body_soup)
            else: # OccupationalTherapy / VisualTherapy
                post_content_div = soup.find('div', class_='post-content')
                summary_box = soup.find('div', style=lambda s: s and 'ebf8ff' in s)
                body_parts = []
                if post_content_div:
                    body_parts.append(str(post_content_div))
                if summary_box:
                    body_parts.append(str(summary_box))
                body_html = '\n'.join(body_parts)
                
            all_articles.append({
                'folder': folder,
                'cat_name': cat_name,
                'cat_badge': cat_badge,
                'cat_slug': cat_slug,
                'cluster': cluster,
                'sub_cluster': sub_cluster,
                'order': order,
                'old_filename': f.name,
                'new_filename': new_filename,
                'title': title,
                'short_topic': short_topic,
                'tags': tags,
                'read_time': read_time,
                'img_src': img_src,
                'caption': caption,
                'summary': summary,
                'citations': citations,
                'date_published': date_published,
                'raw_body': body_html
            })
            
    return all_articles

def build_article_html(art, all_articles):
    folder = art['folder']
    cat_name = art['cat_name']
    cluster_name = art['cluster']
    new_filename = art['new_filename']
    title = art['title']
    summary = art['summary']
    clean_desc = re.sub(r'\s+', ' ', summary).strip().replace('"', '&quot;')[:200]
    keywords_str = ', '.join(art['tags'])
    canonical_url = f"{SITE_BASE_URL}/content/{folder}/{quote(new_filename)}"
    web_page_path = f"/content/{folder}/{new_filename}"
    
    # Filter articles in same cluster for cluster navigation
    cluster_articles = [a for a in all_articles if a['folder'] == folder and a['cluster'] == cluster_name]
    cluster_articles.sort(key=lambda x: x['order'])
    
    # Current index in cluster
    curr_idx = -1
    for idx, ca in enumerate(cluster_articles):
        if ca['new_filename'] == new_filename:
            curr_idx = idx
            break
            
    prev_article = cluster_articles[curr_idx - 1] if curr_idx > 0 else None
    next_article = cluster_articles[curr_idx + 1] if curr_idx < len(cluster_articles) - 1 else None
    
    # Schema.org JSON-LD
    schema_type = "TechArticle" if folder == "DigitalLearning" else "MedicalScholarlyArticle"
    citations_json = [c['text'] for c in art['citations'] if c['text']]
    
    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": [schema_type, "Article"],
                "@id": f"{canonical_url}#article",
                "isPartOf": {
                    "@type": "WebPage",
                    "@id": canonical_url
                },
                "headline": title,
                "description": clean_desc,
                "image": art['img_src'] if art['img_src'] else f"{SITE_BASE_URL}/icons/icon.svg",
                "datePublished": art['date_published'],
                "dateModified": "2026-09-11T09:30:00+08:00",
                "inLanguage": "zh-TW",
                "mainEntityOfPage": canonical_url,
                "author": {
                    "@type": "Person",
                    "name": "蔡泓恩",
                    "alternateName": "Hung-En (Ian) Tsai",
                    "jobTitle": "職能治療師",
                    "url": f"{SITE_BASE_URL}/",
                    "sameAs": [
                        "https://github.com/ian030590",
                        "https://trainerhub.cc"
                    ],
                    "knowsAbout": ["職能治療", "神經復健", "視覺復健", "低視力評估", "數位醫療", "AI系統架構"],
                    "alumniOf": "國立臺灣大學"
                },
                "publisher": {
                    "@type": "Person",
                    "name": "蔡泓恩",
                    "url": f"{SITE_BASE_URL}/"
                },
                "articleSection": cat_name,
                "keywords": art['tags'],
                "citation": citations_json
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "首頁",
                        "item": f"{SITE_BASE_URL}/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "專業文章",
                        "item": f"{SITE_BASE_URL}/blog"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": cat_name,
                        "item": f"{SITE_BASE_URL}/blog?tag={quote(cat_name)}"
                    },
                    {
                        "@type": "ListItem",
                        "position": 4,
                        "name": title,
                        "item": canonical_url
                    }
                ]
            }
        ]
    }
    
    # Render Cluster items
    cluster_items_html = []
    for ca in cluster_articles:
        is_active = (ca['new_filename'] == new_filename)
        active_class = " active" if is_active else ""
        link_target = f"./{ca['new_filename']}"
        current_badge = '<span class="topic-cluster-item-current">目前閱讀中</span>' if is_active else ""
        cluster_items_html.append(f"""
        <li>
          <a href="{link_target}" class="topic-cluster-item{active_class}">
            <span class="topic-cluster-item-num">{ca['order']:03d}</span>
            <span class="topic-cluster-item-title">{ca['title']}</span>
            {current_badge}
          </a>
        </li>""")
        
    cluster_list_rendered = '\n'.join(cluster_items_html)
    
    # Prev Next Navigation
    prev_html = ""
    if prev_article:
        prev_html = f"""
        <a href="./{prev_article['new_filename']}" class="prev-next-card">
          <span class="prev-next-label">
            <span class="material-symbols-outlined" aria-hidden="true">arrow_back</span>
            上一篇（第 {prev_article['order']:03d} 講）
          </span>
          <span class="prev-next-title">{prev_article['title']}</span>
        </a>"""
    else:
        prev_html = """<div class="prev-next-card" style="opacity: 0.5; cursor: default;">
          <span class="prev-next-label">已是專題首篇</span>
          <span class="prev-next-title">沒有上一篇了</span>
        </div>"""
        
    next_html = ""
    if next_article:
        next_html = f"""
        <a href="./{next_article['new_filename']}" class="prev-next-card" style="text-align: right; align-items: flex-end;">
          <span class="prev-next-label">
            下一篇（第 {next_article['order']:03d} 講）
            <span class="material-symbols-outlined" aria-hidden="true">arrow_forward</span>
          </span>
          <span class="prev-next-title">{next_article['title']}</span>
        </a>"""
    else:
        next_html = """<div class="prev-next-card" style="opacity: 0.5; cursor: default; text-align: right; align-items: flex-end;">
          <span class="prev-next-label">已是專題最新篇</span>
          <span class="prev-next-title">敬請期待後續更新</span>
        </div>"""

    # References HTML
    refs_html = ""
    if art['citations']:
        ref_items = []
        for c in art['citations']:
            if c['url']:
                ref_items.append(f'<li><a href="{c["url"]}" target="_blank" rel="noopener noreferrer">{c["text"]}</a></li>')
            else:
                ref_items.append(f'<li>{c["text"]}</li>')
        refs_html = f"""
        <section class="article-references" aria-label="參考文獻與實證指引">
          <h2>參考文獻與實證指引 (References)</h2>
          <ol>
            {chr(10).join(ref_items)}
          </ol>
        </section>
        """

    # Clean body
    cleaned_body = clean_inner_body(BeautifulSoup(art['raw_body'], 'html.parser'))
    
    # Featured image
    figure_html = ""
    if art['img_src']:
        figure_html = f"""
        <figure class="article-featured-figure">
          <img src="{art['img_src']}" alt="{title}" class="article-featured-img" loading="lazy" />
          <figcaption class="article-figcaption">{art['caption'] or title}</figcaption>
        </figure>
        """

    # Published date formatted
    date_str = art['date_published'][:10]
    
    # Evidence badge
    if folder == 'OccupationalTherapy':
        evidence_note = '2026 AHA/ASA 臨床指引實證'
    elif folder == 'VisualTherapy':
        evidence_note = '2023 AAO PPP 臨床指引實證'
    else:
        evidence_note = 'AI 系統架構與工程實踐'

    full_html = f"""<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>{title} | 蔡泓恩 職能治療師</title>
    <meta name="description" content="{clean_desc}" />
    <meta name="keywords" content="{keywords_str}" />
    <meta name="author" content="蔡泓恩 職能治療師" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{canonical_url}" />

    <!-- Open Graph / Social Media -->
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="zh_TW" />
    <meta property="og:site_name" content="蔡泓恩 | 職能治療師" />
    <meta property="og:title" content="{title} ｜ 蔡泓恩 職能治療師" />
    <meta property="og:description" content="{clean_desc}" />
    <meta property="og:url" content="{canonical_url}" />
    <meta property="og:image" content="{art['img_src'] or f'{SITE_BASE_URL}/icons/icon.svg'}" />
    <meta property="article:published_time" content="{art['date_published']}" />
    <meta property="article:modified_time" content="2026-09-11T09:30:00+08:00" />
    <meta property="article:author" content="{SITE_BASE_URL}/" />
    <meta property="article:section" content="{cat_name}" />

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title} ｜ 蔡泓恩 職能治療師" />
    <meta name="twitter:description" content="{clean_desc}" />
    <meta name="twitter:image" content="{art['img_src'] or f'{SITE_BASE_URL}/icons/icon.svg'}" />

    <!-- Favicon & Stylesheet -->
    <link rel="icon" type="image/svg+xml" href="../../icons/icon.svg" />
    <link rel="stylesheet" href="../../css/style.css" />

    <!-- Schema.org Article JSON-LD (E-E-A-T) -->
    <script type="application/ld+json">
{json.dumps(json_ld, ensure_ascii=False, indent=2)}
    </script>
  </head>
  <body>
    <header class="site-header">
      <div class="container nav">
        <a class="brand" href="/">蔡泓恩 | 職能治療師</a>
        <nav class="nav-links" aria-label="主要導覽">
          <a class="nav-link" href="/">首頁</a>
          <a class="nav-link" href="/projects">開源專案</a>
          <a class="nav-link active" href="/blog" aria-current="page">專業文章</a>
          <a class="nav-link" href="/contact">聯絡我</a>
          <a class="nav-link" href="/sponsor">贊助我</a>
        </nav>
        <button
          class="theme-toggle"
          aria-label="切換深色模式"
          title="切換深色模式"
        >
          <span class="material-symbols-outlined icon-dark" aria-hidden="true">dark_mode</span>
          <span class="material-symbols-outlined icon-light" aria-hidden="true" style="display: none;">light_mode</span>
        </button>
        <a class="nav-cta" href="mailto:rainbowh9490@gmail.com">聯絡我</a>
        <button
          class="menu-button"
          aria-label="開啟選單"
          aria-expanded="false"
        >
          <span
            class="animate-icon animate-icon--menu"
            data-animate-icon="menu"
            aria-hidden="true"
          ></span>
        </button>
      </div>
      <div class="mobile-panel">
        <a href="/">首頁</a>
        <a href="/projects">開源專案</a>
        <a href="/blog" aria-current="page">專業文章</a>
        <a href="/contact">聯絡我</a>
        <a href="/sponsor">贊助我</a>
      </div>
    </header>

    <main class="page-main article-page-layout">
      <div class="container">
        <!-- Breadcrumb Navigation -->
        <nav class="breadcrumb-trail" aria-label="文章路徑導覽">
          <a href="/">首頁</a>
          <span class="breadcrumb-separator" aria-hidden="true">/</span>
          <a href="/blog">專業文章</a>
          <span class="breadcrumb-separator" aria-hidden="true">/</span>
          <a href="/blog?tag={quote(cat_name)}">{cat_name}</a>
          <span class="breadcrumb-separator" aria-hidden="true">/</span>
          <span class="breadcrumb-current" aria-current="page">{title}</span>
        </nav>

        <article class="article-container">
          <!-- Article Header -->
          <header class="article-detail-header">
            <div class="article-tag-badges">
              <span class="article-badge">{cat_name}</span>
              <span class="article-badge cluster-badge">{cluster_name}</span>
            </div>
            <h1 class="article-title">{title}</h1>
            <div class="article-meta-row">
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">person</span>
                蔡泓恩 職能治療師
              </span>
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">calendar_today</span>
                {date_str}
              </span>
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">schedule</span>
                {art['read_time']}
              </span>
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">verified</span>
                {evidence_note}
              </span>
            </div>
          </header>

          <!-- Featured Banner Image -->
          {figure_html}

          <!-- Executive Summary Callout Box -->
          <div class="article-lead-box">
            <div class="article-lead-box-title">
              <span class="material-symbols-outlined" aria-hidden="true">lightbulb</span>
              專題重點摘要與核心洞察
            </div>
            <p>{summary}</p>
          </div>

          <!-- Main Body Content -->
          <div class="article-body-content">
            {cleaned_body}
          </div>

          <!-- Scientific References Section -->
          {refs_html}


          <!-- Topic Cluster Series Navigation -->
          <nav class="topic-cluster-nav" aria-label="同系列主題專題叢集">
            <div class="topic-cluster-header">
              <div class="topic-cluster-title">
                <span class="material-symbols-outlined" aria-hidden="true">auto_stories</span>
                【主題叢集】{cluster_name}
              </div>
              <div class="topic-cluster-progress">
                第 {art['order']:03d} 篇 / 全 {len(cluster_articles)} 篇
              </div>
            </div>
            <ul class="topic-cluster-list">
              {cluster_list_rendered}
            </ul>
          </nav>

          <!-- Prev & Next Article Navigation -->
          <div class="prev-next-nav">
            {prev_html}
            {next_html}
          </div>

          <!-- Back to Blog Navigation -->
          <div class="article-bottom-actions">
            <a href="/blog" class="button-secondary">
              <span class="material-symbols-outlined" aria-hidden="true">arrow_back</span>
              返回所有專業專題列表
            </a>
          </div>
        </article>
      </div>
    </main>

    <footer class="site-footer">
      <div class="container footer-grid">
        <div>
          <div class="footer-brand">蔡泓恩 | 職能治療師</div>
          <div class="footer-copy">
            © <span data-year></span> Ian Tsai. 保留所有權利。
          </div>
        </div>
        <div class="footer-links">
          <a href="/">首頁</a>
          <a href="/projects">專案</a>
          <a href="/blog">專業文章</a>
          <a href="/contact">聯絡</a>
          <a href="/sponsor">贊助我</a>
        </div>
      </div>
    </footer>

    <script src="../../js/animate-icons.js"></script>
    <script src="../../js/main.js"></script>
  </body>
</html>"""
    return full_html

def generate_sitemap(all_articles):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{SITE_BASE_URL}/</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/projects</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/blog</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/contact</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/sponsor</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>',
    ]
    
    for art in all_articles:
        folder = art['folder']
        filename = art['new_filename']
        encoded_url = f"{SITE_BASE_URL}/content/{folder}/{quote(filename)}"
        lastmod = "2026-09-11"
        lines.append(f'  <url><loc>{encoded_url}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>')
        
    lines.append('</urlset>\n')
    sitemap_content = '\n'.join(lines)
    SITEMAP_FILE.write_text(sitemap_content, encoding='utf-8')
    print(f'Sitemap written to {SITEMAP_FILE} ({len(all_articles) + 5} URLs)')

def generate_articles_data(all_articles):
    catalog = []
    for art in all_articles:
        catalog.append({
            'id': f"{art['folder']}_{art['order']:03d}",
            'title': art['title'],
            'lead': art['summary'][:160] + ('...' if len(art['summary']) > 160 else ''),
            'imageUrl': art['img_src'],
            'tags': art['tags'],
            'dateString': art['date_published'][:10],
            'readTime': art['read_time'],
            'link': f"/content/{art['folder']}/{art['new_filename']}",
            'sourceName': art['cat_name'],
            'category': art['cat_name'],
            'cluster': art['cluster'],
            'subCluster': art['sub_cluster'],
            'order': art['order'],
            'folder': art['folder'],
            'filename': art['new_filename']
        })
        
    js_code = f"""// Generated static articles catalog (No Blogger dependencies)
window.__STATIC_ARTICLES__ = {json.dumps(catalog, ensure_ascii=False, indent=2)};
"""
    ARTICLES_DATA_FILE.write_text(js_code, encoding='utf-8')
    print(f'Articles data written to {ARTICLES_DATA_FILE} ({len(catalog)} articles)')

def main():
    print('1. Updating CSS tokens and article classes in style.css...')
    update_css()
    
    print('2. Collecting metadata and content for all articles...')
    all_articles = collect_article_metadata()
    print(f'Collected {len(all_articles)} articles across 3 categories.')
    
    print('3. Generating new static HTML pages...')
    for art in all_articles:
        folder = art['folder']
        target_file = CONTENT_DIR / folder / art['new_filename']
        html_code = build_article_html(art, all_articles)
        target_file.write_text(html_code, encoding='utf-8')
        
    print('4. Removing old unrenamed files...')
    for art in all_articles:
        folder = art['folder']
        old_file = CONTENT_DIR / folder / art['old_filename']
        target_file = CONTENT_DIR / folder / art['new_filename']
        if old_file != target_file and old_file.exists():
            old_file.unlink()
            
    print('5. Generating articles-data.js for instant static blog rendering...')
    generate_articles_data(all_articles)
    
    print('6. Generating sitemap.xml...')
    generate_sitemap(all_articles)
    
    print('Build completed successfully!')

if __name__ == '__main__':
    main()
