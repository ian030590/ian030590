# Site development and deployment

共用代理人規則請見 [AGENTS.md](../AGENTS.md)，文章寫作與技術規範請見 [content/README.md](../content/README.md)。根目錄 `README.md` 為 GitHub Profile；本站維護操作集中記錄於本文件。

## 本機開發與建置 ／ Astro

需要 Node.js 22.12 以上（CI 使用 Node.js 24）及 Python 3.12 以上。

```sh
npm ci
python -m pip install -r requirements.txt
npm run dev
```

主要頁面位於 `src/pages/`，共用導覽、頁尾及 SEO 資訊位於 `src/components/` 與 `src/layouts/`。原有 CSS、瀏覽器 JavaScript、圖示及圖片維持在 `css/`、`js/`、`icons/` 與 `assets/`。

`npm run dev`、`npm run check` 與 `npm run build` 會先執行 `python build_static_articles.py`，將文章原檔及公開資產準備到忽略版本控制的 `.generated/public/`，同時產生文章目錄、RSS 與 Sitemap。Astro 從這裡取得公開資產，並輸出完整網站到 `dist/`。文獻原文、維護文件與測試程式不會發布。

文章仍以 `content/` 的既有 HTML 為正式來源，原樣複製，不重新排版或改寫發布日期；新增文章後請重新執行 `npm run prepare:content`，讓開發伺服器更新文章列表。`article_editorial_copy.py` 保留編輯稿供寫作核對，部署流程不會用它覆寫既有文章。

```sh
npm test
npm run check
npm run build
npm run audit:seo
npm run preview
```

建置結束會比對每篇文章原始位元組，並檢查文章導覽、HTML 連結、CSS／JavaScript／圖片路徑、核准標籤、圖片唯一性與 Sitemap。SEO 檢查以 `dist/` 為範圍。原有 `/projects`、`/blog`、`/contact`、`/sponsor` 及 `/content/...html` 路徑保持可用；Cloudflare Pages 會將 `.html` 請求導向對應的簡潔網址。

## GitHub Actions 與 Cloudflare Pages 部署

[部署工作流程](../.github/workflows/seo-audit.yml) 在 PR 與推送至 `main` 時安裝鎖定依賴、測試、檢查型別、建置並執行 SEO 檢查，成功後封裝 `dist/` 為 `astro-dist` artifact。只有 `main` 的推送或手動執行會下載同一份 artifact 並部署，PR 不會部署正式站。

1. 在 Cloudflare Pages 準備名為 `ian030590` 的專案，正式分支設為 `main`。新建時使用 Direct Upload；既有 Git 整合專案請停用 Cloudflare 的自動分支部署，讓 GitHub Actions 成為部署來源，避免兩套流程同時上線。
2. 在 [GitHub Actions Secrets](https://github.com/ian030590/ian030590/settings/secrets/actions) 設定 `CLOUDFLARE_API_TOKEN`（該帳戶的 **Account → Cloudflare Pages → Edit** 權限）及 `CLOUDFLARE_ACCOUNT_ID`。
3. 若專案名稱不同，在同頁面的 Variables 設定 `CLOUDFLARE_PAGES_PROJECT`，預設為 `ian030590`。
4. 推送至 `main`，或在 Actions 選擇 **Astro Build & Cloudflare Pages → Run workflow → main**。檢查 `build` 與 `deploy` 都成功後，再確認正式站。
5. 在 Pages 的 Custom domains 維持 `ian030590.trainerhub.cc`；Astro canonical、RSS 與 Sitemap 皆使用此網址。

Pages 只接收 `dist/`，不需要 Astro server adapter。`_headers` 與 `_redirects` 會隨 artifact 一起部署。首次建立專案、API Token 及 DNS／自訂網域綁定仍須在 Cloudflare 完成。設定細節見 [Cloudflare 官方 CI 部署文件](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/)。

若需從本機手動部署，先執行 `npm run build` 與 `npm run audit:seo`，再於已登入 Wrangler 或設定相同 Cloudflare 環境變數的終端執行 `npm run deploy`。

## SEO 與 Google 索引檢查

`npm run audit:seo` 檢查建置產物；通過代表網站結構符合檢查規則，不代表 Google 已收錄或特定關鍵字排名會提高。新增的 `404.html` 必須保留，讓 Cloudflare Pages 對不存在的網址回傳 404，避免回傳首頁與 HTTP 200；建置同時確認錯誤頁設有 `noindex`。

部署成功後，在已驗證的 Google Search Console 資源中：

1. 提交或重新提交 `https://ian030590.trainerhub.cc/sitemap.xml`，查看 Sitemap 報表的擷取狀態與處理時間。網址檢查中的「暫時性處理錯誤」須搭配這份報表判讀，不能直接當作 XML 格式錯誤。
2. 檢查 `https://ian030590.trainerhub.cc/`，區分「索引中的資料」與「測試實際網址」。先確認最新實際測試可擷取、允許索引、canonical 指向正式首頁，再按「要求建立索引」。
3. 「已檢索－目前尚未建立索引」表示 Google 抓過頁面但尚未納入索引，並不等同 robots.txt 阻擋。保留畫面上的最後檢索時間，後續檢查 Google 是否已重新抓取本次部署。
4. 使用「成效」報表觀察「蔡泓恩」的曝光與點擊。`site:` 查詢與單次一般搜尋只能作為線索，不能取代網址檢查的索引狀態。

目前首頁的主標題包含姓名與職稱，`ProfilePage` 結構化資料連結到同一份 `Person`。這些資訊協助表達頁面主題，不保證收錄。Google 的重新檢索可能需數天至數週，重複要求也不會加快。

若 Cloudflare 回傳 403／1010，先在 Security Events 查明被擋的用戶端；僅更換 User-Agent 的探測不能證明真正的 Googlebot 是否可存取。正式 Google 爬蟲的判定應參照 Search Console 實際測試或已驗證的爬蟲記錄。

官方說明：[要求重新檢索](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)、[Search Console](https://developers.google.com/search/docs/monitor-debug/search-console-start)、[Cloudflare Pages 的 404 與 SPA 行為](https://developers.cloudflare.com/pages/configuration/serving-pages/)。
