---
name: 蔡泓恩｜職能治療師
description: 視覺復健研究、臨床實證文章與開源復健工具的個人網站
colors:
  primary: "#064c86"
  primary-strong: "#003864"
  link: "#0f6cbd"
  link-hover: "#064c86"
  badge-fill: "#deedff"
  canvas: "#f7faff"
  surface: "#ffffff"
  surface-subtle: "#edf4fc"
  ink: "#0a1220"
  ink-secondary: "#3d5068"
  ink-muted: "#526e8e"
  line-subtle: "#d5e4f5"
  line: "#c7d9ee"
  line-strong: "#7694b7"
  error: "#b42318"
  dark-canvas: "#070d18"
  dark-surface: "#0e1726"
  dark-surface-raised: "#142032"
  dark-ink: "#f7faff"
  dark-ink-secondary: "#9bb3d1"
  dark-ink-muted: "#7694b7"
  dark-line: "#233348"
  dark-primary: "#0f6cbd"
  dark-primary-hover: "#064c86"
  dark-link: "#529deb"
  dark-link-hover: "#8ebff6"
  dark-badge-fill: "#002646"
  dark-error: "#fda29b"
typography:
  display:
    fontFamily: "Noto Sans TC, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, PingFang TC, Microsoft JhengHei, sans-serif"
    fontSize: "clamp(36px, 4.2vw, 56px)"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Noto Sans TC, sans-serif"
    fontSize: "clamp(28px, 3vw, 40px)"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.035em"
  title:
    fontFamily: "Noto Sans TC, sans-serif"
    fontSize: "22px"
    fontWeight: 600
    lineHeight: 1.35
  article-heading:
    fontFamily: "Noto Sans TC, sans-serif"
    fontSize: "24px"
    fontWeight: 800
    lineHeight: 1.4
  body:
    fontFamily: "Noto Sans TC, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.75
  article-body:
    fontFamily: "Noto Sans TC, sans-serif"
    fontSize: "18px"
    fontWeight: 500
    lineHeight: 1.85
  label:
    fontFamily: "Noto Sans TC, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.6
rounded:
  sm: "8px"
  control: "9px"
  panel: "10px"
  card: "14px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "48px"
  section: "72px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "11px 20px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.primary-strong}"
    textColor: "{colors.surface}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.link}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
    height: "44px"
  button-secondary-hover:
    backgroundColor: "{colors.badge-fill}"
    textColor: "{colors.link}"
  tag:
    backgroundColor: "{colors.badge-fill}"
    textColor: "{colors.primary-strong}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.card}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "11px 12px"
    height: "46px"
---

# Design System: 蔡泓恩｜職能治療師

## Overview

**Creative North Star: "The Researcher's Notebook"**

這個網站像一本整理得當的研究筆記：紙面明亮，藍色墨水標出該追下去的地方，每一筆紀錄都能回溯來源。視覺權威來自真實內容，包含論文題目、發表日期、作者、DOI 與可開啟的工具，裝飾不參與說服。

版面密度中等偏疏。首頁以不對稱雙欄、細分隔線與可展開的紀錄列組織資訊，文章頁維持單一閱讀動線。動態只回應操作，例如 hover、展開與選單開合，並遵守減少動態偏好。

字級是這套系統的硬性條件。讀者包含低視能與腦傷後視覺、認知受限者，因此版面以重排因應窄螢幕，文字不縮小。

**Key Characteristics:**

- 藍、白、灰藍的單色相系統，沒有漸層。
- Noto Sans TC 單一字族，以字重與尺寸建立層級。
- 研究資料與專案清單以分隔線列表呈現，文章入口才使用卡片。
- 淺色與深色主題共用語意 token，由使用者選擇或系統偏好決定。

## Colors

冷調藍灰墨水在微帶藍的紙面上書寫，藍色只標示可操作與需要注意的位置。

### Primary

- **Notebook Ink Blue**：主要按鈕與品牌強調，hover 時轉為 **Deep Archive Blue**。
- **Annotation Blue**：文字連結、次要按鈕、目前頁面標示與焦點外框，是讀者最常看到的互動色。
- **Index Tab Blue**：標籤與徽章底色，搭配 Deep Archive Blue 文字。

### Neutral

- **Paper Canvas**：全站畫布。
- **Clean Sheet**：卡片、輸入框與浮層表面。
- **Margin Wash**：交替區段、摘要框與次要底色。
- **Carbon Ink / Graphite / Pencil**：主要文字、次要文字與日期等輔助資訊。
- **Ruled Line / Soft Rule / Firm Rule**：卡片外框、細分隔線，以及 hover 與輸入框外框。

### Dark Theme

深色主題以 **Night Desk** 畫布、**Dark Sheet** 卡片與 **Raised Sheet** 浮層的亮度階梯表現層級。互動藍往亮處位移，維持對比。

### Named Rules

**The Blue Ink Rule.** 介面色只用藍、白與灰藍。紅色系僅用於錯誤狀態。

**The No Gradient Rule.** 不使用漸層、光暈或彩色裝飾背景。

**The Frozen Callout Exception.** 文章提示框的紅、橙、綠左邊線屬於既有文章的語意標示，只留在文章內容，不擴散到其他介面。

**The Action Is Not Text Rule.** 按鈕底色 token（`--primary`、`--primary-strong`）只用於填色。強調文字使用 `--color-text-accent` 與 `--color-text-accent-strong`，深色主題才能維持 4.5:1 以上的對比。

## Typography

**Display Font:** Noto Sans TC（fallback：系統無襯線字體、PingFang TC、Microsoft JhengHei）
**Body Font:** Noto Sans TC
**Label/Mono Font:** 同 Noto Sans TC；程式碼使用系統等寬字體

**Character:** 單一字族讓繁體中文保持穩定易讀，層級靠字重與尺寸對比完成，像同一支筆用不同力道書寫。

### Hierarchy

- **Display**：首頁 hero 主標，全頁一次。
- **Headline**：頁面標題與首頁區段標題。
- **Title**：卡片標題與列表項目標題。
- **Article Heading**：文章內 h2；h3 為 20px、字重 700。
- **Body**：介面內文，段落最大寬度約 65ch。
- **Article Body**：文章內文，字重略高以提升長文辨識。
- **Label**：日期、標籤、表單標籤、圖說與導覽輔助資訊。

### Named Rules

**The 16px Floor Rule.** 任何可見中文不得小於 16px，包含圖說、日期、標籤、導覽與產品預覽。

**The Reflow Rule.** 窄螢幕改變欄數與排列，不縮小內文。

## Layout

內容容器最大寬度 1200px，兩側保留 16px，700px 以下為 14px。區段垂直間距為 72px 至 84px，交替使用畫布與 Margin Wash 分段。

編輯型區段使用不對稱雙欄，常見比例為 0.8fr 比 1.2fr 與 1.4fr 比 0.8fr，欄距 48px 至 72px，窄螢幕收合為單欄。文章列表可使用卡片格線，專案頁使用分組清單，聯絡面板以細分隔線區分各項聯絡管道。主要斷點落在 980px、900px、700px 與 640px 附近。

文章頁採無外框的白色閱讀版面，深色主題沿用表面底色。麵包屑、主圖與內文共用一欄，內文寬度為 `--article-measure`（42.75rem），在 18px 字級下每行約 38 個全形字，降低視野缺損與中風後讀者換行時的負擔。

## Elevation & Depth

系統採混合策略：研究列表、學經歷與區段保持平面，以線條與底色分層；卡片、文章主圖與產品預覽使用低而柔和的藍調陰影。深色主題以表面亮度表達高度，陰影僅輔助。

### Shadow Vocabulary

- **Resting Sheet** (`box-shadow: 0 8px 24px rgba(0, 56, 100, 0.08)`)：卡片與文章主圖的靜止狀態。
- **Lifted Sheet** (`box-shadow: 0 16px 36px rgba(0, 56, 100, 0.12)`)：需要提升層級的互動狀態。
- **Dark Resting** (`box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45)`)：深色主題的卡片。

### Named Rules

**The Flat Records Rule.** 研究紀錄、專案清單與學經歷不加陰影，它們是筆記內容，不是浮起的物件。

## Shapes

圓角克制，隨元件尺度遞增：照片、輸入框與表格 8px，按鈕 9px，摘要面板 10px，卡片 14px。全圓角只用於標籤與細指示線。邊框一律 1px，文章提示框的 5px 左邊線是唯一例外。

## Components

### Buttons

沉穩、直接，文字寫明動作。

- **Shape:** 微圓角（9px），最小高度 44px。
- **Primary:** Notebook Ink Blue 底、白字、字重 600。
- **Hover / Focus:** 底色加深；鍵盤焦點為 2px Annotation Blue 外框，offset 2px。
- **Secondary:** 透明底、1px Annotation Blue 邊框，hover 時填入 Index Tab Blue。

### Chips

- **Style:** Index Tab Blue 底、深藍字、全圓角，16px 字重 600。
- **State:** 用於文章分類與專案標籤；首頁學術紀錄不使用膠囊，改用純文字標示類型。

### Cards / Containers

- **Corner Style:** 14px。
- **Background:** Clean Sheet。
- **Shadow Strategy:** Resting Sheet。
- **Border:** 1px Ruled Line，hover 時轉為 Firm Rule，不位移。
- **Internal Padding:** 約 25px，媒體區為 16:9。

### Inputs / Fields

- **Style:** 標籤置於欄位上方，白底、1px Firm Rule 邊框、8px 圓角，最小高度 46px。
- **Focus:** 2px Annotation Blue 外框。
- **Error / Disabled:** 錯誤使用語意紅色與文字說明。

### Navigation

黏性頂部列，高 78px，半透明底搭配 12px 背景模糊。連結為 Graphite，hover 與目前頁面轉為 Annotation Blue，目前頁面帶 2px 底線。980px 以下改為原生 popover 選單。

### Research Record

首頁學術成果的招牌元件：以原生 `details` 組成的分隔線列表，列出類型、等寬數字日期與題目，展開後顯示會議、作者與摘要，動畫 200ms 並遵守減少動態偏好。

### Project Index

專案頁的分組清單：左欄為分組標題，右欄為以 1px 分隔線排列的專案列，窄螢幕收合為單欄。分組依臨床相關性排序，依序為視覺與復健練習、臨床與研究流程、文件與日常工具、開發工具與其他、已封存作品。每列是一個連結，顯示名稱、用途、更新日期與 GitHub 入口，不使用預覽圖或主題標籤。

### Article Reading Column

文章內文 18px、行高 1.85、字重 500，搭配帶圖說的主圖、摘要框、提示框與可水平捲動的表格。

## Do's and Don'ts

### Do:

- **Do** 維持所有可見中文 16px 以上，文章內文 18px 以上。
- **Do** 以真實論文、日期、作者、DOI 與工具內容建立可信度。
- **Do** 使用語意 token，讓新元件同時支援淺色與深色主題。
- **Do** 讓研究紀錄保持平面，以分隔線和字重分層。
- **Do** 讓動態只回應使用者操作，並支援減少動態偏好。
- **Do** 讓互動目標至少 44px，並保留可見的鍵盤焦點。

### Don't:

- **Don't** 使用漸層、光暈、霓虹色或綠、青、紫等非系統色作為介面色。
- **Don't** 加入虛構數據、推薦語、裝飾性插圖或假按鈕。
- **Don't** 用縮小字級解決窄螢幕排版。
- **Don't** 為了樣式調整改寫 `content/` 內未被指名的文章。
- **Don't** 使用自訂游標、自動播放動畫或運動風格的視覺語言。
