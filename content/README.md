# 專業文章撰寫指南與技術規範 (Content Guide & Standards)

本指南規範 `content/` 目錄下所有專業文章的標籤系統（Tags）、檔案命名慣例、排版結構格式、SEO 與 E-E-A-T 結構化資料規範，以及靜態編譯維運流程。

> [!IMPORTANT]
> **AI 助理與協作者必讀**：凡在 `content/` 目錄下新增、修改或重構任何文章，均須嚴格遵守本文件之所有規範，並於更新後執行 `python build_static_articles.py` 完成站點目錄與 Sitemap 的自動編譯。

---

## 一、 目錄結構與三大專題分流

全站專業文章存放於 `content/` 目錄下的三大獨立子目錄：

```text
content/
├── DigitalLearning/      # 數位學習與科技架構專題（AI產品架構思維系列 001~013）
├── OccupationalTherapy/  # 中風神經復健與動作/認知實證專題（001~020）
├── VisualTherapy/        # 視覺復健與低視力輔具實證專題（001~020）
└── README.md             # 本技術與撰寫規範文件
```

---

## 二、 核心標籤系統規範 (Tag System Specification)

為確保搜尋、篩選與分類體系的清晰度與專業度，全站已徹底移除無效、過長或系統雜訊標籤，**嚴格限定僅能使用以下 6 個標準核心標籤**：

### 1. 唯一合法之 6 大標準標籤

| 標籤名稱 | 適用領域與核心定義 | 代表主題 |
| :--- | :--- | :--- |
| **中風復健** | 中風急性期、亞急性期與慢性期神經復健實證介入 | 神經重塑、下床黃金律、偏癱肩防護、失語症、空間忽略 |
| **視覺復健** | 低視力評估、視知覺障礙、偏盲、視野缺損與光學輔具處方 | 2023 AAO指引、微視野與PRL、放大輔具、稜鏡替代、偏心注視 |
| **動作復健** | 上下肢肢體動作控制、步態平衡、肌張力與日常生活功能活動 | CIMT 局限誘發、外骨骼步態、痙攣副木、吞嚥肌群動作、防跌 |
| **認知復健** | 大腦高階執行功能、注意力網絡、空間忽略、語言與情緒調適 | 執行功能訓練、單側空間忽略鑑別、閱讀解碼、中風後憂鬱/焦慮 |
| **數位學習** | 非工程師之科技架構、系統概念、軟體工程與開發流程教學 | 軟體樂高（API/DB/前端/後端）、Vibe Coding 防翻車指南 |
| **AI應用** | 大型語言模型（LLM）、Prompt工程、RAG、Agent與無障礙科技 | 工業級Prompt、外掛大腦RAG、多Agent協同、AI視覺輔具辨識 |

### 2. 多標籤支援原則 (Multi-Tagging Principle)
- **單篇文章可同時具備 1 至多個核心標籤**。
- **跨領域精準標記**：當文章內容跨足多個專業領域時，應精確標記所有涵蓋範疇。例如：
  - 中風空間忽略文章：`["中風復健", "認知復健", "視覺復健"]`
  - 眼球動作控制文章：`["中風復健", "視覺復健", "動作復健"]`
  - 低視力 AI 輔具代償文章：`["視覺復健", "AI應用"]`
  - AI 產品架構教學文章：`["數位學習", "AI應用"]`

### 3. 嚴禁事項 (Prohibitions)
- ❌ **嚴禁自創非標準標籤**（例如：`神經復健`、`職能治療`、`醫學科普`、`科技趨勢`）。
- ❌ **嚴禁將主題叢集或專題名稱當作標籤**（例如：`非工程師的「AI 產品架構思維」12 講專題`、`低視力臨床評估與光學處方科學`）。
- ❌ **嚴禁將系統圖示文字誤當作標籤**（例如：`dark_mode`、`light_mode`）。
- ❌ **標籤文字長度嚴禁超過 10 個字元**。

### 4. 靜態編譯對應表同步維護
每當新增文章時，必須同步在專案根目錄的 [build_static_articles.py](file:///P:/3_WebSite/ian030590/build_static_articles.py) 的 `ARTICLE_TAG_MAP` 字典中登記：
```python
ARTICLE_TAG_MAP = {
    # 範例：目錄名_3位數序號
    "OccupationalTherapy_021": ["中風復健", "動作復健"],
    "VisualTherapy_021": ["視覺復健", "認知復健"],
    ...
}
```

---

## 三、 文章檔案命名規則 (File Naming Conventions)

所有文章檔案必須置於對應子目錄，檔名格式嚴格遵循以下規則：

```text
{3位數序號}_{核心簡稱}_{完整主標題或關鍵字描述}.html
```

### 1. 命名細則
- **3 位數零補齊序號**：必須使用 3 位整數（如 `001_`, `002_`, ..., `020_`），確保檔案在檔案系統、Git 與自動建置腳本中具有穩定的自然排序。
- **底線 `_` 分隔**：序號、簡稱與完整標題之間使用單一底線 `_` 分隔。
- **禁止作業系統衝突字元**：嚴禁使用半形冒號 `:`、全形冒號 `：`、斜線 `/` `\`、半形問號 `?`、全形問號 `？`、引號 `"` `'`、星號 `*`、管道符 `|` 或空白字元。文章標題中原本若有冒號，在檔名中轉換為底線 `_` 或直接連綴。
- **副檔名**：一律為 `.html`。

### 2. 標準範例
- `001_AI產品架構思維系列總覽_非工程師的12講導讀總綱.html`
- `002_上肢動作與精細手功能復健_任務導向訓練、局限誘發療法_CIMT_與_Bobath_技術的實證除魅.html`
- `008_行動智慧時代無障礙轉型_智慧型手機、平板電腦與AI視覺辨識在低視力日常代償之整合應用.html`
- `013_同向偏盲與單側空間忽略的臨床鑑別_感覺輸入缺損與注意力網絡崩解之診斷與處方分野.html`

---

## 四、 文章撰寫格式與排版架構 (Article Layout Architecture)

文章採用語意化 HTML5 編寫，整體版面遵循現代醫學學術期刊與高品質科技專欄標準：

### 1. 頂部導覽路徑 (Breadcrumbs)
```html
<nav class="breadcrumb-trail" aria-label="文章路徑導覽">
  <a href="/">首頁</a>
  <span class="breadcrumb-separator" aria-hidden="true">/</span>
  <a href="/blog">專業文章</a>
  <span class="breadcrumb-separator" aria-hidden="true">/</span>
  <a href="/blog?tag=中風復健">中風復健</a>
  <span class="breadcrumb-separator" aria-hidden="true">/</span>
  <span class="breadcrumb-current" aria-current="page">{文章完整標題}</span>
</nav>
```

### 2. 文章標頭 (Article Detail Header)
包含可點擊之標籤按鈕、主題叢集標章、主標題與專業元數據：
```html
<header class="article-detail-header">
  <div class="article-tag-badges">
    <!-- 各核心標籤以超連結呈現，點擊可直接篩選該標籤所有文章 -->
    <a href="/blog?tag=中風復健" class="article-badge" title="查看「中風復健」相關文章">中風復健</a>
    <a href="/blog?tag=動作復健" class="article-badge" title="查看「動作復健」相關文章">動作復健</a>
    <span class="article-badge cluster-badge">{主題叢集系列名稱}</span>
  </div>
  <h1 class="article-title">{文章完整標題}</h1>
  <div class="article-meta-row">
    <span class="article-meta-item">
      <span class="material-symbols-outlined" aria-hidden="true">person</span>
      蔡泓恩 職能治療師
    </span>
    <span class="article-meta-item">
      <span class="material-symbols-outlined" aria-hidden="true">calendar_today</span>
      2026-09-11
    </span>
    <span class="article-meta-item">
      <span class="material-symbols-outlined" aria-hidden="true">schedule</span>
      約 5 分鐘閱讀
    </span>
    <span class="article-meta-item">
      <span class="material-symbols-outlined" aria-hidden="true">verified</span>
      2026 AHA/ASA 臨床指引實證
    </span>
  </div>
</header>
```

### 3. 首圖與圖說 (Featured Figure & Figcaption)
> [!CAUTION]
> **圖床禁令**：**嚴格禁止使用 `files.catbox.moe`**。該網域會觸發院內網路（NTUH/TANet）防火牆之 TCP Reset 封鎖破圖。必須使用經全球 CDN 驗證之 Unsplash 高解析度醫療/科技攝影照片，並附帶優化參數 `?auto=format&fit=crop&w=1200&q=80`。

```html
<figure class="article-featured-figure">
  <img src="https://images.unsplash.com/photo-...?auto=format&fit=crop&w=1200&q=80" alt="{圖片替代文字}" class="article-featured-img" loading="lazy" />
  <figcaption class="article-figcaption">{精準圖說與實證臨床圖解說明}</figcaption>
</figure>
```

### 4. 核心導讀摘要方塊 (Executive Summary Callout Box)
放置於首圖下方、內文之前，提煉核心臨床價值或技術洞察：
```html
<div class="article-lead-box">
  <div class="article-lead-box-title">
    <span class="material-symbols-outlined" aria-hidden="true">lightbulb</span>
    專題重點摘要與核心洞察
  </div>
  <p>{3~5 行文字精準摘要：背景痛點、核心機制、指引推薦或工程解方}</p>
</div>
```

### 5. 內文排版元件規範 (Body Content Elements)
- **標題層級**：內文主標題使用 `<h2>`，子章節使用 `<h3>`，深層段落使用 `<h4>`。不得跳級使用。
- **提示方塊（Callouts）**：
  - 一般重點：`<div class="callout-box"><p>...</p></div>`
  - 實證指引 / 強推薦：`<div class="callout-box success"><p>...</p></div>`
  - 臨床注意事項：`<div class="callout-box amber"><p>...</p></div>`
  - 禁用告警 / 傷害警示：`<div class="callout-box warning"><p>...</p></div>`
- **數據與比對表格**：表格必須具備 `class="article-table"` 並由 `<div class="table-wrapper">` 包覆，以支援響應式左右捲動：
  ```html
  <div class="table-wrapper">
    <table class="article-table">
      <thead>
        <tr><th>指標項目</th><th>傳統做法</th><th>最新實證指引</th></tr>
      </thead>
      <tbody>
        <tr><td>...</td><td>...</td><td>...</td></tr>
      </tbody>
    </table>
  </div>
  ```
- **代碼與終端機區塊**：`<div class="code-terminal-block"><pre><code>...</code></pre></div>`

### 6. 參考文獻與 DOI 規範 (References & Active DOI Standard)
> [!IMPORTANT]
> **嚴格實證與有效 DOI 要求**：
> 1. 每一篇醫學與科技專題文章均須附有實證參考文獻列表。
> 2. 嚴禁假 DOI（如 `10.1177/15459683211011234` 佔位符）或未正式出版之草稿號（如 Cochrane `pub4` 尚未刊登者應使用 `pub3`）。
> 3. 所有 DOI 必須使用正式標準格式 `<a href="https://doi.org/..." target="_blank" rel="noopener noreferrer">`，並確保能解析跳轉至期刊官網（HTTP 301/302 -> 200）。
> 4. 嚴禁雙重協定筆誤（如 `https://doi.org/https://doi.org/...`）。

```html
<section class="article-references" aria-label="參考文獻與實證指引">
  <h2>參考文獻與實證指引 (References)</h2>
  <ol>
    <li>
      <a href="https://doi.org/10.1016/S0140-6736(17)31447-2" target="_blank" rel="noopener noreferrer">
        Lindley RI, Anderson CS, Billot L, et al. Family-led rehabilitation after stroke in India (ATTEND): a randomised controlled trial. Lancet. 2017;390(10094):588-599.
      </a>
    </li>
  </ol>
</section>
```

### 7. 主題叢集與前後篇導覽 (Topic Cluster & Prev/Next Navigation)
由 `build_static_articles.py` 自動注入：
- `<nav class="topic-cluster-nav" aria-label="同系列主題專題叢集">`：顯示該叢集所有篇章，並標註「目前閱讀中」。
- `<div class="prev-next-nav">`：上一篇與下一篇之專屬導航按鈕卡片。

---

## 五、 Metadata 與 SEO / E-E-A-T 規範

文章 HTML `<head>` 必須配置完整的 SEO 與 E-E-A-T 結構化中繼資料：

### 1. 基礎標籤與規範網址
- **全站 Base URL**：`https://ian030590.trainerhub.cc`（禁止出現 `ian030590.github.io`）。
- **Canonical**：`<link rel="canonical" href="https://ian030590.trainerhub.cc/content/{目錄}/{檔名}" />`
- **Keywords**：`<meta name="keywords" content="{由核准標籤組成的逗號分隔清單}" />`

### 2. 社群中繼標籤 (Open Graph & Twitter Card)
```html
<meta property="og:type" content="article" />
<meta property="og:locale" content="zh_TW" />
<meta property="og:site_name" content="蔡泓恩 | 職能治療師" />
<meta property="og:title" content="{文章標題} ｜ 蔡泓恩 職能治療師" />
<meta property="og:description" content="{純文字摘要}" />
<meta property="og:url" content="https://ian030590.trainerhub.cc/content/{目錄}/{檔名}" />
<meta property="og:image" content="{Unsplash 首圖 URL}" />
<meta property="article:published_time" content="{ISO8601 時間字串}" />
<meta property="article:author" content="https://ian030590.trainerhub.cc/" />
<meta property="article:section" content="{主分類名稱}" />

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{文章標題} ｜ 蔡泓恩 職能治療師" />
<meta name="twitter:description" content="{純文字摘要}" />
<meta name="twitter:image" content="{Unsplash 首圖 URL}" />
```

### 3. Schema.org JSON-LD (E-E-A-T 強化)
- **分類型別**：
  - 醫療與職能治療文章：`"@type": ["MedicalScholarlyArticle", "Article"]`
  - 科技與數位學習文章：`"@type": ["TechArticle", "Article"]`
- **作者背書**：
  - 姓名：蔡泓恩（Hung-En (Ian) Tsai）
  - 頭銜：職能治療師
  - 學歷：國立臺灣大學
  - 領域背書（knowsAbout）：`["職能治療", "神經復健", "視覺復健", "低視力評估", "數位醫療", "AI系統架構"]`
- **文獻收錄**：在 `citation` 陣列中列出所有參考文獻文字。
- **麵包屑導航**：在 `BreadcrumbList` 節點中建立完整的層級路徑。

---

## 六、 撰寫與發布標準作業程序 (SOP)

每當新增或修改文章時，請遵循以下 5 步驟標準流程：

1. **查閱規範**：每次撰寫前必先閱讀本規範 `content/README.md`。
2. **檔案撰寫**：在 `content/` 下對應子目錄建立符合命名規則之 HTML 檔案。
3. **圖床與 DOI 查核**：確認首圖為 Unsplash 高清圖，且參考文獻內所有 DOI 均經即時驗證為可訪問有效連結。
4. **登記標籤**：在 `build_static_articles.py` 的 `ARTICLE_TAG_MAP` 中新增該篇之標準標籤（限 6 大合法標籤）。
5. **執行靜態建置**：
   ```powershell
   python build_static_articles.py
   ```
   檢查 `js/articles-data.js` 與 `sitemap.xml`，並確認 `blog.html` 前端顯示正常。
