# 專業文章撰寫指南與技術規範 (Content Guide & Standards)

本指南規範 `content/` 目錄下所有專業文章的標籤系統（Tags）、檔案命名慣例、排版結構格式、SEO 與 E-E-A-T 結構化資料規範，以及靜態編譯維運流程。

> [!IMPORTANT]
> **AI 助理與協作者必讀**：凡在 `content/` 目錄下新增、修改或重構任何文章，均須嚴格遵守本文件之所有規範，並於更新後執行 `python build_static_articles.py` 完成站點目錄與 Sitemap 的自動編譯。

---

## 文章寫作原則：人性化科普與忠實呈現研究

本節適用於標題、摘要、正文、圖說及搜尋與社群描述。下方 HTML 範例僅規範技術元件，不要求各篇使用相同的標題句型、段落數或敘事順序。

### 讀者與敘事

- 醫療文章以科普衛教為主，從讀者的生活困難或疑問切入，以自然、尊重且容易理解的繁體中文說明；專業名詞首次出現時簡要解釋。數位學習文章採易懂的科技解說，不硬套醫療敘事。
- 每篇依主題獨立撰寫主標題、段落標題與摘要。禁止整批套用「臨床問題／指引如何建議／研究如何支持／四個重點」或另一組固定句型；也不要只替換疾病與療法名稱。
- 依內容安排段落、結尾、表格與圖解，不為湊齊固定版型重複資訊。生活情境若為假設或作者示例，須明確標示，不冒充真實個案或研究受試者。
- 採台灣臨床術語；不把困難直接歸因於懶惰、缺乏動機或不配合，也不以恐嚇、煽情或療效保證吸引閱讀。

### 原文核對與證據界線

- 撰寫前優先閱讀 `content/References/` 內與主題相符的文獻。沒有適用來源時，查閱正式論文或官方文件；不得只依既有文章、摘要或 AI 生成內容推斷研究結論。
- 保留影響解讀的研究族群、病程、樣本數、介入與對照條件、追蹤時間、測量結果及限制。數字與結論需核對原文，不為易讀而省略會改變原意的條件。
- 區分指引建議、原始試驗、系統性回顧與作者實務應用。只從指引得知的研究須標明「依指引整理」，不得聲稱已閱讀該試驗全文；原始研究的直接引用需另查原文。
- 保留推薦強度與不確定性；「可考慮」不可改成「必須」，相關性不可改成因果，無顯著差異不可改成完全等效，測驗進步不可直接改成生活功能恢復。呈現與問題相關的陰性或不一致結果。
- 避免「黃金律」「突破性治癒」「保證恢復」「全面有效」等超出證據的詞彙。標題、摘要和圖說也須遵守相同界線，不將研究成果擴大為特定產品背書。
- 引用放在對應主張附近，文獻編號、頁碼與章節須指向真正支持該句的來源。跨族群、跨病因與跨國制度的外推限制須說明；不得直接將國外照護制度當成台灣規範。

### 編輯稿與建置同步

- 已登錄於根目錄 `article_editorial_copy.py` 的 `HUMANIZED_ARTICLE_COPY` 之文章，其標題、摘要與正文由該編輯稿提供。修改時須更新對應項目，不能只修改會被建置覆寫的 HTML。
- 未登錄的文章仍依對應 HTML 維護；不要為了新增文章而複製固定的敘事模板。
- 文章內容變更後執行 `python build_static_articles.py`，確認可見標題、摘要、正文、引用、OG／Twitter、JSON-LD、文章列表與前後篇導覽一致。
- 結構檢查通過不代表研究原意或所有外部連結都已驗證。來源無法取得或網站拒絕自動存取時，應如實記錄核對範圍，不宣稱全部驗證成功。

---

## 一、 目錄結構與四大專題分流

全站專業文章存放於 `content/` 目錄下的四大獨立子目錄：

```text
content/
├── DigitLearn/           # 臨床數位能力、Excel/Python 與 AI 應用專題（001~028）
├── MotorRehab/           # 中風動作、移動與併發症管理專題（001~016）
├── CognitRehab/          # 中風認知、溝通與社會參與專題（001~010）
├── VisualRehab/          # 低視能及腦傷後視覺復健實證專題（001~024）
├── References/           # 撰寫前須核對的研究與指引原文
└── README.md             # 本技術與撰寫規範文件
```

---

## 二、 核心標籤系統規範 (Tag System Specification)

為確保搜尋、篩選與分類體系的清晰度與專業度，全站已徹底移除無效、過長或系統雜訊標籤，**嚴格限定僅能使用以下 6 個標準核心標籤**：

### 1. 唯一合法之 6 大標準標籤

| 標籤名稱 | 適用領域與核心定義 | 代表主題 |
| :--- | :--- | :--- |
| **中風復健** | 中風急性期、亞急性期與慢性期神經復健實證介入 | 神經重塑、下床黃金律、偏癱肩防護、失語症、空間忽略 |
| **視覺復健** | 低視能評估、視知覺障礙、偏盲、視野缺損與光學輔具處方 | 2023 AAO指引、微視野與PRL、放大輔具、稜鏡替代、偏心注視 |
| **動作復健** | 上下肢肢體動作控制、步態平衡、肌張力與日常生活功能活動 | CIMT 局限誘發、外骨骼步態、痙攣副木、吞嚥肌群動作、防跌 |
| **認知復健** | 大腦高階執行功能、注意力網絡、空間忽略、語言與情緒調適 | 執行功能訓練、單側空間忽略鑑別、閱讀解碼、中風後憂鬱/焦慮 |
| **數位學習** | 非工程師之科技架構、系統概念、軟體工程與開發流程教學 | 軟體樂高（API/DB/前端/後端）、Vibe Coding 防翻車指南 |
| **AI應用** | 大型語言模型（LLM）、Prompt工程、RAG、Agent與無障礙科技 | 工業級Prompt、外掛大腦RAG、多Agent協同、AI視覺輔具辨識 |

### 2. 多標籤支援原則 (Multi-Tagging Principle)
- **單篇文章可同時具備 1 至多個核心標籤**。
- **跨領域精準標記**：當文章內容跨足多個專業領域時，應精確標記所有涵蓋範疇。例如：
  - 中風空間忽略文章：`["中風復健", "認知復健", "視覺復健"]`
  - 眼球動作控制文章：`["中風復健", "視覺復健", "動作復健"]`
  - 低視能 AI 輔具代償文章：`["視覺復健", "AI應用"]`
  - AI 產品架構教學文章：`["數位學習", "AI應用"]`

### 3. 嚴禁事項 (Prohibitions)
- ❌ **嚴禁自創非標準標籤**（例如：`神經復健`、`職能治療`、`醫學科普`、`科技趨勢`）。
- ❌ **嚴禁將主題叢集或專題名稱當作標籤**（例如：`非工程師的「AI 產品架構思維」12 講專題`、`低視能臨床評估與光學處方科學`）。
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

## 三、 專有名詞與臨床術語使用規範 (Terminology & Glossary Standards)

為維持台灣醫療臨床、職能治療復健、低視能輔具與科技專欄的專業度與用語在地化標準，避免使用非正式翻譯、中國大陸慣用語或容易引發混淆之詞彙，所有文章在撰寫、翻譯、擴充或修訂時，**必須嚴格遵循以下專有名詞對照表**。

> [!TIP]
> **持續更新機制**：本表將隨臨床標準、特教/身障輔具法規與技術演進持續擴充維護。AI 助理與撰寫者每次產出內容時，必須主動依照本對照表核對術語。

### 1. 專有名詞規範對照表 (Terminology Mapping)

| 錯誤／禁用用語 (❌) | 正確／官方標準用語 (⭕) | 英文對應詞 (English) | 領域範疇 | 規範說明與臨床緣由 |
| :--- | :--- | :--- | :--- | :--- |
| **電子助視器** | **電子擴視機** | Electronic Video Magnifier / CCTV | 視覺復健／輔具科學 | 台灣身心障礙輔具補助基準、臨床眼科與驗光學術界統一採用「電子擴視機」（含桌上型擴視機、可攜式電子擴視機），「電子助視器」多為中國大陸或非正式直譯用語。 |
| **智慧頭顯** | **頭戴式顯示器** | Head-Mounted Display (HMD) / Smart Glasses | 科技應用／數位輔具 | 「頭顯」為中國網路簡稱縮寫，正式繁體中文與台灣科技學界標準全稱為「頭戴式顯示器」（或依功能稱「智慧眼鏡」）。 |
| **低視力** | **低視能** | Low Vision | 視覺復健／眼科醫學 | 台灣眼科醫學會、特殊教育界、視覺復能臨床及國際 AAO 繁體在地化標準術語統一採用「低視能」，強調的是視覺「功能（Function）」受損而非僅純粹視力數值（Acuity），故以「低視能」為準確專業用語。 |
| **黃斑旁預覽視窗** | **中央凹旁預視視窗** | Parafoveal Preview Window | 視覺復健／神經眼科學 | 閱讀眼動機制中，「Parafoveal」指視網膜中央凹（Fovea）周圍的旁中央凹/中央凹旁區域，「Preview」在認知心理學與眼動閱讀研究中標準學術譯名為「預視」而非「預覽」。「黃斑旁預覽視窗」為非正式直譯，臨床與認知神經科學標準術語統一採用「中央凹旁預視視窗」。 |

### 2. 未來詞彙擴充與維護準則 (Expansion Guidelines)
- 若遇新興科技、臨床研究或跨國指引翻譯，優先查閱：
  1. 衛生福利部「身心障礙者輔具費用補助辦法」輔具基準表
  2. 中華民國眼科醫學會、台灣職能治療學會官方臨床指引與期刊
  3. 國家教育研究院雙語詞彙、學術名詞暨辭書資訊網
- 嚴禁未經在地化審核直接引進未轉換之中國科技或醫學術語（如：頭顯、抓手、賦能[非職能治療empowerment場合濫用]、閉環等）。

---

## 四、 文章檔案命名規則 (File Naming Conventions)

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
- `008_行動智慧時代無障礙轉型_智慧型手機、平板電腦與AI視覺辨識在低視能日常代償之整合應用.html`
- `013_同向偏盲與單側空間忽略的臨床鑑別_感覺輸入缺損與注意力網絡崩解之診斷與處方分野.html`

---

## 五、 文章撰寫格式與排版架構 (Article Layout Architecture)

文章採用語意化 HTML5 編寫，以科普衛教與易讀科技解說為內容方向，保留可追溯的研究引用。以下元件規範可共用，文章標題與敘事結構須依主題獨立設計：

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
包含可點擊之核心標籤、主標題與專業元數據：
```html
<header class="article-detail-header">
  <div class="article-tag-badges">
    <!-- 各核心標籤以超連結呈現，點擊可直接篩選該標籤所有文章 -->
    <a href="/blog?tag=中風復健" class="article-badge" title="查看「中風復健」相關文章">中風復健</a>
    <a href="/blog?tag=動作復健" class="article-badge" title="查看「動作復健」相關文章">動作復健</a>
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

## 六、 Metadata 與 SEO / E-E-A-T 規範

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
  - 領域背書（knowsAbout）：`["職能治療", "神經復健", "視覺復健", "低視能評估", "數位醫療", "AI系統架構"]`
- **文獻收錄**：在 `citation` 陣列中列出所有參考文獻文字。
- **麵包屑導航**：在 `BreadcrumbList` 節點中建立完整的層級路徑。

---

## 七、 撰寫與發布標準作業程序 (SOP)

每當新增或修改文章時，請遵循以下 5 步驟標準流程：

1. **查閱規範**：每次撰寫前必先閱讀本規範 `content/README.md`（包含標籤、命名與專有名詞對照表）。
2. **原文核對與撰寫**：先閱讀 `content/References/` 中適用的原文；依本文件的寫作原則撰寫。已登錄的文章更新 `article_editorial_copy.py` 對應編輯稿，其餘文章在 `content/` 對應子目錄維護符合命名規則的 HTML。
3. **圖床與 DOI 查核**：確認首圖為 Unsplash 高清圖，且參考文獻內所有 DOI 均經即時驗證為可訪問有效連結。
4. **登記標籤**：在 `build_static_articles.py` 的 `ARTICLE_TAG_MAP` 中新增該篇之標準標籤（限 6 大合法標籤）。
5. **執行靜態建置**：
   ```powershell
   python build_static_articles.py
   ```
   檢查 `js/articles-data.js` 與 `sitemap.xml`，並確認 `blog.html` 前端顯示正常。
