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
8. **Link Integrity & Conflict Prevention（連結完整性與檔名防衝突檢驗）**:
   - Every internal link in `blog.html`, `js/articles-data.js`, `sitemap.xml`, and within each article (breadcrumbs, prev/next navigation, cluster links) MUST point to an existing, valid static file on disk (0 tolerance for 404 broken links).
   - Filenames must NEVER contain cloud-sync conflict suffixes (e.g., `[conflicted]`, `[conflicted 2]`) or spaces.
   - The build script `build_static_articles.py` automatically validates all generated links and cleans/fails on broken links or conflict files.
9. **Publish Date & Chronological Sorting（實際撰寫日期發布）**:
   - All newly created, added, or revised articles MUST use the real, actual date of authorship as their publish date (`datePublished`, `article:published_time`, `dateModified`, `article:modified_time`, formatted as `YYYY-MM-DDT08:00:00+08:00`).
   - NEVER reuse or copy obsolete placeholder dates from batch templates (e.g., `2026-09-12`). The blog and home feed dynamically sort articles descending by publish date to identify and feature the latest article as "最新專題" (Index 0). Accurately dating new articles is mandatory.
10. **Zero Overwrite & Non-Destructive Addition（嚴禁覆蓋既有舊文章，一律撰寫新篇章）**:
   - 嚴禁修改、改寫、重構或覆蓋磁碟與 Git 上既有的舊文章（Zero Overwrite）。
   - 凡是根據新需求、新文獻（如教科書新章節）或新專題撰寫文章，**一律必須使用全站未曾使用之全新序號撰寫獨立的新檔案**（接續於當前目錄最大序號之後，如 `029_...`）。
   - 嚴禁插入舊文章序號區間（避免重新計算前後篇導覽而連帶竄改舊文章內容，進而引發雲端同步衝突或破壞歷史版本）。
   - 新增專題時，若有系列導覽需求，應在 `build_static_articles.py` 中劃分獨立的主題叢集（Cluster），確保既有舊文章之導覽鏈與內文 100% 保持乾淨零變更（Git 零 Diff）。

## 文章寫作原則：人性化科普與忠實呈現研究

- **文件位置**：專案開發與維護規範以本文件、GEMINI.md 與 content/README.md 為準；根目錄 README.md 亦同步揭示「不覆蓋舊文章」之核心維護原則。
- **嚴禁改動舊文章**：任何新專題或文獻整理皆為增量擴充，絕對不可修改或覆蓋既有舊文章。所有新文章必須使用新序號獨立發布，保持既有舊文章 100% 完整不變。
- **讀者與語氣**：醫療文章以科普衛教為主，用自然、尊重且容易理解的繁體中文，從讀者的生活困難或疑問切入；專業名詞首次出現時簡要解釋。數位學習文章採易懂的科技解說，不硬套醫療敘事。
- **獨立標題與結構**：每篇依實際主題撰寫主標題、段落標題與摘要，不使用共用句型或固定的「臨床問題／指引／研究／四個重點」模板。段落數、結尾、表格與圖解由內容需要決定；共用 HTML 樣式不代表共用文章敘事。
- **五大核心提問聚焦**：撰寫或重構文章時，必須在思維與論述上向內容提出五個問題，並確認文章有確實回答：(1) 目前有什麼臨床困境（或實務痛點）、(2) 研究建議如何處理、(3) 處理後可以預期的效果是什麼、(4) 這個處理適合誰使用、(5) 具體應該做什麼。**嚴禁將這五個問題直接變成段落標題**，標題必須依實際主題獨立命名，但內文必須自然且明確地回答這五個核心問題。
- **先讀原文**：優先閱讀 `content/References/` 內與主題相關的文獻；沒有相符來源時，查閱正式論文或官方文件。不得只憑既有文章、摘要或 AI 生成內容推斷研究結論。
- **忠實還原**：保留研究族群、介入與對照條件、追蹤時間、測量結果及重要限制。區分指引建議、原始試驗、回顧與作者應用；透過指引得知的研究，須標明為指引整理，不假裝已讀該試驗全文。
- **避免誇大與非保守斷言**：不使用「保證恢復」「全面有效」「突破性治癒」等超出證據的用詞；保留「可能」「可考慮」「證據有限」等原意。除非指引或文獻證據非常確切（如列為 Harm 級傷害之明確醫療禁忌），否則文章中不可任意使用「禁止」、「禁用」等非保守斷言詞彙，應使用「建議避免」、「不建議」或「建議優先考慮」等客觀審慎之保守臨床用語。相關性不寫成因果、無顯著差異不寫成完全等效、測驗進步不直接寫成生活功能恢復。
- **可追溯與在地化**：引用應緊鄰支持的主張，頁碼、章節與文獻編號須對應正確來源；不把其他國家的照護制度直接當成台灣規範。假設情境須明確標示，不冒充真實個案或研究結果。
- **真實發布日期**：文章 metadata（HTML meta 標籤、JSON-LD 與內文 `<time>`）必須按實際撰寫完成之當日日期發布，嚴禁沿用舊模板日期導致「最新專題」無法正常輪替更新。
- **維護與驗證**：遵循 [完整文章規範](content/README.md)。若文章已登錄於 `article_editorial_copy.py` 的 `HUMANIZED_ARTICLE_COPY`，須修改對應編輯稿，避免只改 HTML 而被建置覆蓋。文章更新後執行 `python build_static_articles.py`，確認內文、標題、摘要、OG／Twitter、JSON-LD 與導覽一致。

## 學術與科普寫作邏輯框架（杜絕突兀感、鬆散感與語感薄弱）

文章若缺少因果推導與背景鋪陳，會產生「開頭突兀、說教感強烈、內容破碎鬆散、主軸模糊」的致命缺點。所有專業科普文章必須嚴格遵循以下五大學術寫作、篇章語言學與科學傳播框架：

1. **John Swales 的 CARS 模型（Create a Research Space Model）**：
   - **Move 1：Establishing a Territory（確立論述疆域／背景鋪陳）**：開篇必須先建立科學／病理生理背景（如中風後神經網絡受損、能量調節與神經化學改變），建立讀者共識基礎。嚴禁首段缺少病理情境、連「中風」或核心疾病都未提及就直接跳入生活情境。
   - **Move 2：Establishing a Niche（建立論述縫隙／認知衝突）**：明確指出臨床實務與日常照護上的認知落差（如家屬常把大腦器質性神經疲勞誤解為個案意志消沉、消極或不配合）。
   - **Move 3：Occupying the Niche（填補縫隙／展開解方）**：在 Move 1 與 Move 2 確立後，才自然開展本文的鑑別維度、評估重點與介入對策。嚴禁在缺少 Move 1 與 2 時直接空降 Move 3（處方指令）。

2. **Randy Olson 的 ABT 敘事弧線（And, But, Therefore Framework）**：
   - 科學傳播必須具備因果張力動能，杜絕「沒有 AND、沒有 BUT，直接從 THEREFORE 開始」的命令式寫法。
   - **AND（背景常態）**：中風會造成大腦神經網絡損傷，**而且（AND）**生活參與需要大腦動機與生理能量系統支援。
   - **BUT（認知衝突）**：**但是（BUT）**，照護者看見躺床叫不動，常直覺指責為個案不努力，忽視了神經疲勞、憂鬱與睡眠障礙的生理交織。
   - **THEREFORE（推論解方）**：**因此（THEREFORE）**，評估時不能急著苛責動機，而應先客觀記錄改變並系統性鑑別。

3. **篇章語言學的「已知—未知契約」（The Given-New Contract, Haviland & Clark / Joseph Williams）**：
   - 每個段落與句子的開端必須立足於讀者「已知（Given）」的舊資訊或已鋪陳的背景，再逐步引導至「未知（New）」的新資訊或處方。
   - 嚴禁用突兀的祈使句（如「先描述改變，不急著責怪意願」）或未交代病史背景的角色（如「一個原本喜歡園藝的人」）突兀開場，避免資訊斷層與說教感。

4. **科學新聞學的「焦點段理論」（The Nut Graph Framework）**：
   - 在引言或案例場景之後、各項細部指引與數據量表之前，必須具備承重牆般的 Nut Graph（焦點段落）。
   - 必須清楚回答：**本質是什麼？大腦或科學機制是什麼？為什麼這對讀者的生活至關重要？**
   - 缺乏 Nut Graph 會導致後續各章節淪為零散碎片，文章失去核心主軸。

5. **認知心理學：破除「知識的詛咒」（Curse of Knowledge）與「過早處方」（Premature Prescription）**：
   - 治療師常因自身太熟悉病理機轉，而將「大腦神經損傷 ➔ 生理機能改變 ➔ 家屬直覺誤解」的因果推導鏈自動省略，直接對讀者下達臨床指導指令。
   - 必須將完整的「因果機轉鏈」寫出來，讀者才能在認知上接納並理解處方的合理性。
