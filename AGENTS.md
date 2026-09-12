# Agent Instructions & Content Generation Rules

## 📌 MANDATORY INSTRUCTION FOR CONTENT CREATION & EDITING

**Whenever you are tasked with creating, modifying, editing, translating, or reviewing ANY article under the `content/` directory, you MUST first read [content/README.md](file:///P:/3_WebSite/ian030590/content/README.md) using the `view_file` tool and strictly follow all of its guidelines.**

### Core Requirements:
1. **Tags**:
   - Strictly limited to the 6 approved tags: `中風復健`, `視覺復健`, `動作復健`, `認知復健`, `數位學習`, `AI應用`.
   - Multi-tagging is supported and encouraged for interdisciplinary topics.
   - Do NOT create any new custom tags or use long cluster titles as tags.
   - Always register the tags in `ARTICLE_TAG_MAP` in `build_static_articles.py`.
2. **File Naming**:
   - Must follow: `{3位數序號}_{核心簡稱}_{完整主標題或關鍵字描述}.html`.
   - No colons, slashes, quotation marks, or spaces in filenames.
3. **Hero Images**:
   - NEVER use `files.catbox.moe` (blocked by hospital/academic networks).
   - Use high-quality, verified Unsplash CDN URLs.
4. **Citations & DOIs**:
   - Every scientific reference must have a working, verified, clickable official DOI (`<a href="https://doi.org/..." target="_blank" rel="noopener noreferrer">`).
   - Zero tolerance for fake DOIs, outdated draft suffixes (e.g. pub4 before publication), or double-protocol typos (`https://doi.org/https://`).
5. **Metadata & Base URL**:
   - Site URL is strictly `https://ian030590.trainerhub.cc`.
   - Include complete Open Graph, Twitter Cards, and Schema.org JSON-LD E-E-A-T metadata.
6. **Build Process**:
   - Run `python build_static_articles.py` to regenerate static article pages, `js/articles-data.js`, and `sitemap.xml`.
7. **Terminology & Glossary**:
   - Strictly follow the terminology mapping table in [content/README.md](file:///P:/3_WebSite/ian030590/content/README.md):
     - `電子助視器` (❌) -> `電子擴視機` (⭕)
     - `智慧頭顯` (❌) -> `頭戴式顯示器` (⭕)
     - `低視力` (❌) -> `低視能` (⭕)
     - `黃斑旁預覽視窗` (❌) -> `中央凹旁預視視窗` (⭕)
   - Adhere strictly to Taiwanese medical and assistive technology clinical standards.

## 文章寫作原則：人性化科普與忠實呈現研究

- **文件位置**：根目錄 README.md 是 GitHub Profile，禁止在其中新增或修改文章撰寫規範；文章規範維護於本文件、GEMINI.md 與 content/README.md。
- **讀者與語氣**：醫療文章以科普衛教為主，用自然、尊重且容易理解的繁體中文，從讀者的生活困難或疑問切入；專業名詞首次出現時簡要解釋。數位學習文章採易懂的科技解說，不硬套醫療敘事。
- **獨立標題與結構**：每篇依實際主題撰寫主標題、段落標題與摘要，不使用共用句型或固定的「臨床問題／指引／研究／四個重點」模板。段落數、結尾、表格與圖解由內容需要決定；共用 HTML 樣式不代表共用文章敘事。
- **先讀原文**：優先閱讀 `content/References/` 內與主題相關的文獻；沒有相符來源時，查閱正式論文或官方文件。不得只憑既有文章、摘要或 AI 生成內容推斷研究結論。
- **忠實還原**：保留研究族群、介入與對照條件、追蹤時間、測量結果及重要限制。區分指引建議、原始試驗、回顧與作者應用；透過指引得知的研究，須標明為指引整理，不假裝已讀該試驗全文。
- **避免誇大**：不使用「保證恢復」「全面有效」「突破性治癒」等超出證據的用詞；保留「可能」「可考慮」「證據有限」等原意。相關性不寫成因果、無顯著差異不寫成完全等效、測驗進步不直接寫成生活功能恢復。
- **可追溯與在地化**：引用應緊鄰支持的主張，頁碼、章節與文獻編號須對應正確來源；不把其他國家的照護制度直接當成台灣規範。假設情境須明確標示，不冒充真實個案或研究結果。
- **維護與驗證**：遵循 [完整文章規範](content/README.md)。若文章已登錄於 `article_editorial_copy.py` 的 `HUMANIZED_ARTICLE_COPY`，須修改對應編輯稿，避免只改 HTML 而被建置覆蓋。文章更新後執行 `python build_static_articles.py`，確認內文、標題、摘要、OG／Twitter、JSON-LD 與導覽一致。
