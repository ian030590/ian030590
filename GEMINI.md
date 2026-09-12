# 專案規則與內容維護守則 (Project Rules & Content Guidelines)

## 📌 撰寫文章最高優先原則 (Mandatory Article Writing Rule)

**凡是涉及撰寫、新增、修改、擴充或重構 `content/` 目錄下的任何文章，AI 助理或協作代理人「必須」首先使用 `view_file` 讀取並嚴格遵循 [content/README.md](file:///P:/3_WebSite/ian030590/content/README.md) 的完整規範。**

### 核心規範摘要：
1. **標籤系統（Tags）**：
   - 全站**嚴格僅能使用 6 個官方標籤**：`中風復健`、`視覺復健`、`動作復健`、`認知復健`、`數位學習`、`AI應用`。
   - 支援多標籤（Multi-tag），視文章涵蓋範疇精準標註。
   - 嚴禁自創標籤（如 `職能治療`、`神經復健`）、嚴禁過長標籤（如專題叢集名稱）、嚴禁抓取介面圖示字串（如 `dark_mode`）。
   - 新增文章必須同步在 [build_static_articles.py](file:///P:/3_WebSite/ian030590/build_static_articles.py) 的 `ARTICLE_TAG_MAP` 中登記。
2. **檔案命名規範（Naming）**：
   - 格式：`{3位數序號}_{核心簡稱}_{完整主標題或關鍵字描述}.html`（如 `001_二十年中風復健典範轉移_從經驗主義到高強度神經重塑與急性期下床黃金律.html`）。
   - 嚴禁在檔名中使用冒號 `:`、`：`、斜線、引號、問號或空格。
3. **圖片圖床規範（Images）**：
   - **嚴禁使用 `files.catbox.moe`**（會觸發醫院與學術網路防火牆封鎖破圖）。
   - 必須使用經全球 CDN 驗證之 Unsplash 高解析度專業圖檔。
4. **參考文獻與 DOI 規範（Citations）**：
   - 醫學與科技文章必須附有真實實證參考文獻。
   - 所有 DOI 必須使用標準格式 `<a href="https://doi.org/..." target="_blank" rel="noopener noreferrer">`，且必須經 Crossref/PubMed 檢驗為可正常訪問之官方永久連結（100% 拒絕 404 與假 DOI 佔位符）。
5. **站點網址與 SEO / E-E-A-T（Metadata）**：
   - 站點 Base URL 統一為 `https://ian030590.trainerhub.cc`（禁止出現 `ian030590.github.io`）。
   - 配置完整 Canonical、Open Graph、Twitter Card 與 Schema.org JSON-LD（`MedicalScholarlyArticle` / `TechArticle`，作者蔡泓恩 職能治療師）。
6. **靜態建置標準流程（Build SOP）**：
   - 每次撰寫或修改文章後，必須於終端執行：
     ```powershell
     python build_static_articles.py
     ```
   - 確保文章自動整合進入 [js/articles-data.js](file:///P:/3_WebSite/ian030590/js/articles-data.js) 與 [sitemap.xml](file:///P:/3_WebSite/ian030590/sitemap.xml)。
7. **專有名詞使用規範（Terminology Standards）**：
   - 嚴格遵守 [content/README.md](file:///P:/3_WebSite/ian030590/content/README.md) 第三節之專有名詞對照表，未來持續更新：
     - `電子助視器` (❌) ➔ `電子擴視機` (⭕)
     - `智慧頭顯` (❌) ➔ `頭戴式顯示器` (⭕)
     - `低視力` (❌) ➔ `低視能` (⭕)
     - `黃斑旁預覽視窗` (❌) ➔ `中央凹旁預視視窗` (⭕)
   - 遵循台灣臨床醫學、視覺復健與特教輔具標準在地化用語，杜絕非標準直譯或大陸流行縮寫。

## 文章寫作原則：人性化科普與忠實呈現研究

- **文件位置**：根目錄 README.md 是 GitHub Profile，禁止在其中新增或修改文章撰寫規範；文章規範維護於本文件、AGENTS.md 與 content/README.md。
- **讀者與語氣**：醫療文章以科普衛教為主，用自然、尊重且容易理解的繁體中文，從讀者的生活困難或疑問切入；專業名詞首次出現時簡要解釋。數位學習文章採易懂的科技解說，不硬套醫療敘事。
- **獨立標題與結構**：每篇依實際主題撰寫主標題、段落標題與摘要，不使用共用句型或固定的「臨床問題／指引／研究／四個重點」模板。段落數、結尾、表格與圖解由內容需要決定；共用 HTML 樣式不代表共用文章敘事。
- **先讀原文**：優先閱讀 `content/References/` 內與主題相關的文獻；沒有相符來源時，查閱正式論文或官方文件。不得只憑既有文章、摘要或 AI 生成內容推斷研究結論。
- **忠實還原**：保留研究族群、介入與對照條件、追蹤時間、測量結果及重要限制。區分指引建議、原始試驗、回顧與作者應用；透過指引得知的研究，須標明為指引整理，不假裝已讀該試驗全文。
- **避免誇大**：不使用「保證恢復」「全面有效」「突破性治癒」等超出證據的用詞；保留「可能」「可考慮」「證據有限」等原意。相關性不寫成因果、無顯著差異不寫成完全等效、測驗進步不直接寫成生活功能恢復。
- **可追溯與在地化**：引用應緊鄰支持的主張，頁碼、章節與文獻編號須對應正確來源；不把其他國家的照護制度直接當成台灣規範。假設情境須明確標示，不冒充真實個案或研究結果。
- **維護與驗證**：遵循 [完整文章規範](content/README.md)。若文章已登錄於 `article_editorial_copy.py` 的 `HUMANIZED_ARTICLE_COPY`，須修改對應編輯稿，避免只改 HTML 而被建置覆蓋。文章更新後執行 `python build_static_articles.py`，確認內文、標題、摘要、OG／Twitter、JSON-LD 與導覽一致。
