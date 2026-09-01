# 蔡泓恩 Hung-En (Ian) Tsai 🏥🛠️

**職能治療背景 · 數位復能與辦公自動化工具開發者 — 把臨床評估需求與工作流痛點，轉化為開源、流暢且易用的軟體工具。**
**Occupational therapy background · Digital health & workflow automation developer — turning clinical assessment needs and daily workflow bottlenecks into open-source, usable tools.**

Keywords: occupational therapy · clinical assessment · digital health · telerehabilitation · motor & cognitive training · office automation · workflow tools · Python · TypeScript · React · Electron · Cloudflare

- 🏥 **臨床與數位復能** — 職能治療背景，開發涵蓋動作協調、視覺功能（眼動/蓋伯斑塊/哈特圖）、認知注意（UFOV/反應抑制）與口腔訓練之全方位數位復能平台與臨床收案系統
- 🛠️ **辦公與研究自動化** — 開發醫學文獻自動化追蹤（PubMed / Zotero AI）、文件批次處理（PDF / 影像多格式轉換）、門診叫號推播與人體工學健康提醒
- ⚡ **全端與軟硬體整合** — 從 Arduino 動作震顫量測儀器、Chrome 擴充功能、Electron 桌面應用到 Cloudflare 無伺服器架構

[![Platform](https://img.shields.io/badge/Platform-trainerhub.cc-005eb8?style=flat-square&logo=cloudflare&logoColor=white)](https://trainerhub.cc)
[![GitHub](https://img.shields.io/badge/GitHub-ian030590-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/ian030590)
[![Email](https://img.shields.io/badge/Email-rainbowh9490%40gmail.com-1c1917?style=flat-square&logo=gmail&logoColor=white)](mailto:rainbowh9490@gmail.com)

---

## 我在做什麼 ／ What I build

工具皆從臨床實務、研究流程與辦公日常痛點出發——評估繁瑣、資料重複輸入、文獻整理耗時或流程卡住，就寫工具把它打通。

- **🏃 數位復能與臨床評估** — 動作協調（急躁棒震顫分析/手勢/塔防）、視覺功能（眼動/蓋伯斑塊/RSVP閱讀/哈特圖）、認知訓練（UFOV/反應時間/高階推理）、口腔訓練平台與 Steam 式隔離遊戲執行架構
- **🏥 臨床醫療與照護工作流** — 臺大醫院低視力門診收案與復能追蹤、門診即時叫號通知系統（Chrome Extension & Electron 桌面版）
- **📚 醫學研究與文獻工作流** — PubMed 定期自動檢索、Zotero 論文 AI 結構化摘要、關節活動度（ROM）與人體工學姿勢角度計算
- **💼 辦公與效率自動化工具** — PDF 批次合併/解密/單頁分割、多格式檔案萬用轉換（HEIC/PNG/JPG/PDF）、人體工學定時強制休息鬧鐘、影音下載轉碼工具

## 工具與作品 ／ Projects

### 🏥 數位復能與臨床評估 / Occupational Therapy & Clinical Tools

| 專案 | 做什麼 |
|---|---|
| 🏃 [**RehabTrainerHub**](https://github.com/ian030590/RehabTrainerHub) | **居家訓練網 ([trainerhub.cc](https://trainerhub.cc))** — 整合動作（塔防/手勢/追蹤）、視覺（蓋伯斑塊/RSVP閱讀/哈特圖/眼動）、認知（UFOV/反應時間/高階推理）、口腔訓練的數位復能平台；具備 5 重安全隔離（獨立網域、嚴格 Iframe 沙盒、CSP 阻斷外連、MessageChannel 通訊、人工審核）與單一遊戲 PWA 安裝的 Steam 式 jsPsych 遊戲發布環境。 |
| ⚡ [**BuzzwireAnalyzer**](https://github.com/ian030590/BuzzwireAnalyzer) | **電流急躁棒動作穩定度與協調度分析儀** — 結合 Arduino 1000 Hz 類比電壓取樣與 Python Tkinter GUI，自動去彈跳並量化震顫次數、接觸時長與接觸佔比，自動輸出圖表化 Excel 評估報告。 |
| 👁️ [**AssessmentSimulation**](https://github.com/ian030590/AssessmentSimulation) | **臨床視覺與認知評估模擬工具** — 提供眼動控制評估（追視、跳視、固視穩定性 OMT）與周邊視野/注意力評估（UFOV 處理速度、分散注意、選擇注意）動態模擬。 |
| 📐 [**AngleCalculator**](https://github.com/ian030590/AngleCalculator) | **關節活動度與姿勢角度計算工具** — 專為職能治療 ROM 評估、人體工學姿勢分析設計之三角函數自動換算與常模比對試算表。 |
| 👁️ [**NTUHLowvision**](https://github.com/ian030590/NTUHLowvision) | **臺大醫院低視力收案與復能系統** — 整合初診、門診紀錄、視力驗光、視覺功能、功能視覺、輔具評估與復能追蹤等自動化表單與病歷檢索。 |

### 🏥 臨床工作流與研究助理 / Clinical Workflow & Research Utilities

| 專案 | 做什麼 |
|---|---|
| 🔔 [**NTUHNotifier**](https://github.com/ian030590/NTUHNotifier) | **臺大醫院門診看診進度通知 (Chrome 擴充功能)** — 背景定期查詢門診即時叫號，在目標號碼接近時發出瀏覽器桌面推播提醒。 |
| 🖥️ [**NTUHNotifier2**](https://github.com/ian030590/NTUHNotifier2) | **臺大醫院門診叫號桌面通知器** — 基於 Electron + React 19 + TypeScript 打造的桌面應用，常駐系統工具列即時監控看診進度。 |
| 📚 [**ResearchAssistant**](https://github.com/ian030590/ResearchAssistant) | **醫學文獻自動化研究助理** — 包含 PubMed 定時自動檢索推播（PubmedSeeker）與 Zotero 書目庫 + LLM 論文核心結構化摘要（PaperReviewer）之 n8n 工作流。 |
| ⏰ [**WinteruptiveAlarm**](https://github.com/ian030590/WinteruptiveAlarm) | **Windows 強制中斷式人體工學休息鬧鐘** — 常駐系統工具列，定時跨所有螢幕觸發全螢幕伸展提醒，防止久坐與視力疲勞，支援任意鍵快速解除。 |
| 🎵 [**PitchIdentifier**](https://github.com/ian030590/PitchIdentifier) | **網頁音訊即時音高辨識 (Chrome 擴充功能)** — 使用 Web Audio API 自相關演算法，零延遲即時捕捉分頁音訊並即時辨識基頻、音高（MIDI Note）與音域範圍。 |

### 💼 辦公自動化與效率工具 / Office & Productivity Utilities

| 專案 | 做什麼 |
|---|---|
| 🔄 [**FormatConverter**](https://github.com/ian030590/FormatConverter) | **萬用多格式批次檔案轉換工具箱** — 支援 HEIC、PNG、JPG、BMP、WEBP、TIFF、PDF 互相轉換之整合終端 CLI 與獨立轉換模組。 |
| 📑 [**PDFCombiner**](https://github.com/ian030590/PDFCombiner) | **PDF 批次合併工具** — 自動掃描目錄內所有 PDF 檔案，按自然檔名順序合併輸出為單一文件。 |
| 🔓 [**PDFDecrypter**](https://github.com/ian030590/PDFDecrypter) | **PDF 密碼移除與解鎖工具** — 快速解除受密碼保護之 PDF 文件列印、複製與修改限制，純本機離線處理保證資料安全。 |
| ✂️ [**PDFSeparater**](https://github.com/ian030590/PDFSeparater) | **PDF 單頁批次分割工具** — 自動將多頁 PDF 拆解為一頁一個獨立檔案並依序命名歸檔。 |
| 🛠️ [**UtilitiesInstaller**](https://github.com/ian030590/UtilitiesInstaller) | **便攜型工具一鍵部署器** — 支援雲端下載、MSI 靜默安裝、BAT 背景執行與桌面捷徑自動建立。 |
| 🎚️ [**WAVnormalizer**](https://github.com/ian030590/WAVnormalizer) | **批次音訊音量標準化工具** — 免 VST 伴奏最佳化工具，支援單聲道拓寬、Opto 動態壓縮與 EBU R128（-14 LUFS / -1 dBTP）廣播級正規化。 |
| 🎬 [**YTDownloader**](https://github.com/ian030590/YTDownloader) | **YouTube 高音質影音下載與轉碼器** — 一鍵下載高畫質影片與無損/高音質 Opus/M4A 音訊，內建 FFmpeg 轉碼封裝。 |

## 專業領域與技術架構 ／ Tech Stack & Engineering

| 領域 | 核心技術與應用 |
|---|---|
| 🏥 **復健科技與臨床評估** | 職能治療（OT）、動作協調訓練、視覺功能評估（OMT / Gabor Patch / RSVP / Hart Chart）、認知測驗（UFOV / Reaction Time / Executive Function）、jsPsych 8.x SDK、臨床收案流程 |
| ⚡ **應用與跨平台開發** | Python（Tkinter / Pandas / PyPDF / Matplotlib）、TypeScript、React 19、Electron、Vite、Tailwind CSS、Chrome Extension (Manifest V3)、n8n |
| ☁️ **雲端與無伺服器架構** | Cloudflare Pages / Workers / Functions、D1 (SQLite)、R2 (Object Storage)、KV、Turborepo / npm workspaces、Google Apps Script |
| 🔌 **軟硬體整合與音訊工程** | Arduino 韌體感測、Web Audio API、Audio Worklet、聲音訊號處理（EBU R128 / Loudnorm / Dynamic Compression） |

---

📍 Taipei, Taiwan · 🎓 National Taiwan University · 🌐 [trainerhub.cc](https://trainerhub.cc) · ✉️ [rainbowh9490@gmail.com](mailto:rainbowh9490@gmail.com)
