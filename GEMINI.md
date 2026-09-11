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
