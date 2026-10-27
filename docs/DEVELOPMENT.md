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

文章仍以 `content/` 的既有 HTML 為同步來源，原樣複製，不重新排版或改寫發布日期。文章列表載入後會透過 `/api/articles` 取得 Blogger 公開文章與原生標籤，全文在本站 `/article?id=...` 閱讀；API 暫時無法使用時保留本站靜態文章目錄。新增文章後請重新執行 `npm run prepare:content`，更新這份備援目錄、RSS 與 Sitemap。`article_editorial_copy.py` 保留編輯稿供寫作核對，部署流程不會用它覆寫既有文章。

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

## Blogger 文章同步與列表

[`blogger.config.json`](../blogger.config.json) 設定 Blog ID `8849463716377519690`、repository 與同步速度。API key 只能讀取公開文章，寫入需要擁有此部落格權限的 Google 帳號授權 OAuth scope `https://www.googleapis.com/auth/blogger`。

### 一次性授權與憑證儲存

1. 在 Google Cloud 專案啟用 Blogger API v3，建立 OAuth client 並設定同意畫面。如果是 Web application client，加入 redirect URI `http://127.0.0.1:8765/`。若應用程式為 External / Testing，加入自己的帳號為測試使用者；Google 對這類測試應用程式的 refresh token 通常僅保留 7 天，長期排程應完成適當的正式發布設定。
2. 執行 `npm run blogger:auth`，輸入 client ID、client secret，並在開啟的 Google 頁面登入授權。腳本會使用 state 與 PKCE 核對回應，將 refresh token 寫入 `.blogger/credentials.json`，不印出 token。
3. 在已登入 GitHub CLI 的終端執行 `python -B scripts/blogger_auth.py --github-secrets`，上傳 `BLOGGER_CLIENT_ID`、`BLOGGER_CLIENT_SECRET`、`BLOGGER_REFRESH_TOKEN` 至 repository 的加密 Actions Secrets。也可以在 [GitHub Secrets 設定](https://github.com/ian030590/ian030590/settings/secrets/actions) 手動設定。Secrets 不會寫入 Git 檔案。
4. 在本機 `.blogger/credentials.json` 加入 `api_key` 欄位，再執行 `python -B scripts/blogger_auth.py --worker-secret`，將它設定為 Cloudflare Worker 的 `BLOGGER_API_KEY` secret。Blogger API key 不需要上傳 GitHub。此 key 必須允許伺服器端請求；使用 HTTP referrer 限制的 key 不適用 Worker，可限制為僅能呼叫 Blogger API。

`.blogger/`、`.dev.vars` 與 `.env*` 均已被 Git 忽略，建置也不會發布它們。憑證不得放進 `blogger.config.json`、workflow YAML 或公開 JavaScript。更換憑證時重新執行對應上傳指令；本機檔案應留在自己的電腦。

### 每次 push 與分批接續

[`Sync articles to Blogger`](../.github/workflows/blogger-sync.yml) 是伺服器端的 push hook。任何電腦推送至 `main` 都會觸發；PR 與其他分支不會修改 Blogger。它另於 UTC 00:37／06:37／12:37／18:37（台灣時間 08:37／14:37／20:37／02:37）接續待處理文章。GitHub 排程可能延遲。

- 每次最多 5 次寫入，每次寫入前等待至少 120 秒，不平行發文；一般一批約需 10 分鐘。沒有變更時不寫入，也不等待。
- 初次 41 篇匯入需要 9 批，排程會逐批完成。後續只處理文字、標籤、日期或檔案內容有變更的文章。
- 每篇遠端文章的 HTML 包含 repository、來源 ID 與雜湊標記。重跑會重新讀取遠端標記，跳過已完成的文章；即使上次建立成功後連線中斷，也能避免重複建立。發現重複來源標記時停止，交由人工查核。
- 同步以最新 `main` 為準，工作流程依序執行，不會取消正在寫入的一批。中途失敗的進度由遠端標記保留。
- 遇到 HTTP 403 或 429 立即停止，將至少 24 小時冷卻狀態寫入 Actions cache，後續執行先檢查冷卻期。`Retry-After` 秒數若更長則採用它。cache 可能被 GitHub 淘汰，因此每批第一次寫入仍會等待 120 秒。其他失敗也停止，寫入不自動重試。
- 這些設定是降低頻率的措施，Google 沒有承諾任何固定速度能避免垃圾內容判定或帳號限制。持續 403 時，先在 Google Cloud／Blogger 查明權限或限制原因。

可在 Actions 手動執行工作流程：`apply=false`（預設）只列出新增／更新／刪除數量，`apply=true` 才會寫入一批。本機可執行：

```sh
python -B scripts/blogger_sync.py --export-only
npm run blogger:plan
npm run blogger:sync
```

第一個指令完全不連網；後兩個指令使用本機被忽略的憑證，或同名 `BLOGGER_CLIENT_ID`／`BLOGGER_CLIENT_SECRET`／`BLOGGER_REFRESH_TOKEN` 環境變數。不要在 Actions 執行的同時從本機寫入，以免兩個執行者同時建立文章。

### 內容所有權、刪除與回復

同步只讀取原始 HTML，不會改寫 `content/`。Blogger 文章保留全文、配圖、引用和原發布日期；文章內部的相對連結轉為本站的完整網址，原有 `/content/...html`、RSS 與 Sitemap 維持可用。Blogger 內文附有範圍限定的排版 CSS，不套用整站樣式到 Blogger 主題。

網站分類直接採用 Blogger 回傳的 `labels`，不限制為本機六個標籤；同步新增的文章會先沿用原有標籤。後續更新會保留在 Blogger 額外新增的標籤。本機來源內容未變更時，也不會覆蓋在 Blogger 手動修改的標題、文字或標籤；來源下次修改時，以本機全文為準。

本機刪除來源後，同步會將具有本 repository 標記的對應遠端文章移到垃圾桶。手動建立或其他來源的 Blogger 文章不會被刪除。已改成草稿的遠端文章無法使用 Blogger 的垃圾桶 API，同步會停止並要求人工處理該篇，避免永久刪除。若本機文章清單完全為空，預設中止；確定要移除全部同步文章時才於本機執行 `python -B scripts/blogger_sync.py --apply --allow-empty`。

復原時先停用同步 workflow，再從 Blogger 垃圾桶還原文章或還原來源檔案。重新啟用前執行 dry run，確認不會再次移除。若要回復網站為靜態列表，可移除 `js/main.js` 中 `/api/articles` 的載入區段；原有靜態列表仍保留。停用本地 OAuth 授權可至 Google 帳號撤銷應用程式權限。

Worker 會一次讀完所有 Blogger 分頁，公開列表快取 5 分鐘；成功回傳空清單時顯示「目前還沒有公開文章」，不將已刪除的遠端文章混回結果。瀏覽器只從遠端 HTML 擷取純文字和 HTTP(S) 圖片網址，卡片內容皆跳脫後顯示。API key 留在 Worker，OAuth 憑證只供同步程式使用。本機完整測試需先 build，再執行 `npx wrangler dev`，並在 `.dev.vars` 設定 `BLOGGER_API_KEY`；`astro dev`／`astro preview` 沒有 Worker API，會顯示靜態備援列表。

全文閱讀頁同樣使用 Blogger API，不依賴 Blogger 自訂網域能否開啟；目前 `blog.trainerhub.cc` 首頁回傳 404，需另於 Blogger 後台檢查自訂網域設定。全文透過 DOMPurify 清理，移除腳本、事件處理、任意樣式、表單及嵌入頁面，並套用本站文章樣式。閱讀頁的通用入口設為 `noindex`；原有靜態文章仍保留原本的 canonical、結構化資料、RSS 與 Sitemap。

官方文件：[Blogger 授權與讀寫](https://developers.google.com/blogger/docs/3.0/using)、[文章標籤與 HTML 欄位](https://developers.google.com/blogger/docs/3.0/reference/posts)、[刪除與垃圾桶](https://developers.google.com/blogger/docs/3.0/reference/posts/delete)、[OAuth refresh token](https://developers.google.com/identity/protocols/oauth2/web-server)。

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
