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

建置結束會比對每篇文章原始位元組，並檢查文章導覽、HTML 連結、CSS／JavaScript／圖片路徑、核准標籤、圖片唯一性與 Sitemap。SEO 檢查以 `dist/` 為範圍。原有 `/projects`、`/blog`、`/contact`、`/sponsor` 及 `/content/...html` 路徑保持可用；Cloudflare Workers 會將 `.html` 請求導向對應的簡潔網址。

## GitHub Actions 與 Cloudflare Workers 部署

[部署工作流程](../.github/workflows/seo-audit.yml) 在 PR 與推送至 `main` 時安裝鎖定依賴、測試、檢查型別、建置並執行 SEO 檢查，成功後封裝 `dist/` 為 `astro-dist` artifact。只有 `main` 的推送或手動執行會下載同一份 artifact，以 `wrangler deploy` 部署到 Cloudflare Workers；PR 不會部署正式站。

網站以 [Workers 靜態資產](https://developers.cloudflare.com/workers/static-assets/) 提供，設定集中在 [`wrangler.jsonc`](../wrangler.jsonc)：

- Worker 名稱為 `ian`，靜態頁面全部來自 `dist/`，不需要 Astro server adapter。`run_worker_first: ["/api/*"]` 讓只有 `/api/*` 執行 [`worker/index.js`](../worker/index.js)，其餘請求直接由靜態資產回應。
- `html_handling: auto-trailing-slash` 讓 `/projects` 提供 `projects.html`，`/projects.html` 轉址到 `/projects`，與原本 Pages 的簡潔網址相同（轉址狀態碼為 307）。
- `not_found_handling: 404-page` 讓不存在的網址回傳 `404.html` 與 HTTP 404。
- `workers_dev` 與 `preview_urls` 關閉，只有自訂網域 `ian030590.trainerhub.cc` 與 `ian.trainerhub.cc` 提供網站，避免重複內容被收錄。網域以 `custom_domain` 綁定，部署時一併確認。

`_headers` 與 `_redirects` 隨 `dist/` 部署，由 Workers 讀取為設定，不會成為公開檔案。

1. 在 [GitHub Actions Secrets](https://github.com/ian030590/ian030590/settings/secrets/actions) 設定 `CLOUDFLARE_API_TOKEN` 與 `CLOUDFLARE_ACCOUNT_ID`。API Token 使用 Cloudflare 的 **Edit Cloudflare Workers** 範本建立，Account Resources 選本帳戶，Zone Resources 選 `trainerhub.cc`，讓部署可以更新 Worker 與自訂網域。
2. 推送至 `main`，或在 Actions 選擇 **Astro Build & Cloudflare Workers → Run workflow → main**。檢查 `build` 與 `deploy` 都成功後，再確認正式站。
3. Astro canonical、RSS 與 Sitemap 皆使用 `https://ian030590.trainerhub.cc`。新增自訂網域時，該主機名稱不能已有其他 DNS 記錄；先在 Cloudflare DNS 刪除舊記錄，再加入 `wrangler.jsonc` 的 `routes` 並部署。

不要在 Cloudflare 的 Workers Builds 連結這個 Git repository，讓 GitHub Actions 維持唯一部署來源，避免兩套流程同時上線。

若需從本機手動部署，先執行 `npm run build` 與 `npm run audit:seo`，再於已登入 Wrangler（`npx wrangler login`）或設定相同 Cloudflare 環境變數的終端執行 `npm run deploy`。Windows 若開啟 Git `core.autocrlf`，本機建置的文章會帶 CRLF 換行，與 CI 產物位元組不同；正式部署以 GitHub Actions 為準。

### 聯絡表單與 Resend 寄信

`/contact` 的表單送到 `POST /api/contact`，由 Worker 檢查欄位、來源網域、隱藏防垃圾欄位與每個 IP 每分鐘 3 次的頻率限制（`CONTACT_RATE_LIMITER`），再透過 [Resend](https://resend.com/docs/api-reference/emails/send-email) 寄到 `CONTACT_TO_EMAIL`。信件的回覆地址設為訪客填寫的信箱，在郵件軟體按「回覆」即可直接回信。Resend API Key 只存放在 Cloudflare secret，不寫入程式碼或瀏覽器端 JavaScript。

1. 在 Resend 建立 API Key，權限選 **Sending access**。
2. 在已登入 Wrangler 的終端執行 `npx wrangler secret put RESEND_API_KEY`，貼上 API Key。secret 只需設定一次，之後的部署會保留。
3. 寄件與收件地址設定在 `wrangler.jsonc` 的 `vars`。預設寄件地址 `onboarding@resend.dev` 是 Resend 的測試網域，只能寄到 Resend 帳號的註冊信箱；若收件地址不同，先在 Resend 驗證自有網域（例如 `trainerhub.cc`），再把 `CONTACT_FROM_EMAIL` 改成該網域的地址。
4. 缺少 API Key 或地址設定時表單回傳 503，並請訪客改寄 Email。

本機測試：`npm run dev` 不會執行 Worker。先執行 `npm run build`，在忽略版本控制的 `.dev.vars` 寫入 `RESEND_API_KEY=...`，再執行 `npx wrangler dev`。`npm test` 會以模擬的 Resend 回應檢查 Worker。

## SEO 與 Google 索引檢查

`npm run audit:seo` 檢查建置產物；通過代表網站結構符合檢查規則，不代表 Google 已收錄或特定關鍵字排名會提高。新增的 `404.html` 必須保留，讓 Cloudflare Workers 對不存在的網址回傳 404，避免回傳首頁與 HTTP 200；建置同時確認錯誤頁設有 `noindex`。

部署成功後，在已驗證的 Google Search Console 資源中：

1. 提交或重新提交 `https://ian030590.trainerhub.cc/sitemap.xml`，查看 Sitemap 報表的擷取狀態與處理時間。網址檢查中的「暫時性處理錯誤」須搭配這份報表判讀，不能直接當作 XML 格式錯誤。
2. 檢查 `https://ian030590.trainerhub.cc/`，區分「索引中的資料」與「測試實際網址」。先確認最新實際測試可擷取、允許索引、canonical 指向正式首頁，再按「要求建立索引」。
3. 「已檢索－目前尚未建立索引」表示 Google 抓過頁面但尚未納入索引，並不等同 robots.txt 阻擋。保留畫面上的最後檢索時間，後續檢查 Google 是否已重新抓取本次部署。
4. 使用「成效」報表觀察「蔡泓恩」的曝光與點擊。`site:` 查詢與單次一般搜尋只能作為線索，不能取代網址檢查的索引狀態。

目前首頁的主標題包含姓名與職稱，`ProfilePage` 結構化資料連結到同一份 `Person`。這些資訊協助表達頁面主題，不保證收錄。Google 的重新檢索可能需數天至數週，重複要求也不會加快。

若 Cloudflare 回傳 403／1010，先在 Security Events 查明被擋的用戶端；僅更換 User-Agent 的探測不能證明真正的 Googlebot 是否可存取。正式 Google 爬蟲的判定應參照 Search Console 實際測試或已驗證的爬蟲記錄。

官方說明：[要求重新檢索](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)、[Search Console](https://developers.google.com/search/docs/monitor-debug/search-console-start)、[Cloudflare Workers 靜態資產的 404 與 HTML 處理](https://developers.cloudflare.com/workers/static-assets/routing/)。
