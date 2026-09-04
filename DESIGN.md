# Design System: 蔡泓恩｜職能治療師

## Visual direction

An airy clinical portfolio: calm, precise, and medically credible. Density is 4/10, variance is 4/10, and motion is limited to useful interaction feedback. Measured whitespace and quiet structural lines connect occupational therapy, research, and software without athletic cues or dashboard clutter.

## Colour palette & Token architecture

Strict clinical discipline: use only blue, white, slate, and black values. No gradients, green, teal, purple, or neon.

### 1. Primitive HEX Scales (基礎色彩數列)

All steps are strictly monotonic in relative luminance to ensure mathematical predictability.

#### Clinical Slate Scale (冷霧灰藍中性色階)
| Token | HEX | Luminance | Primary Role |
| :--- | :--- | :--- | :--- |
| `--slate-50` | `#F7FAFF` | 0.9537 | Light Canvas Background / Dark Inverted Primary Text |
| `--slate-100` | `#EDF4FC` | 0.8973 | Light Surface Subtle / Soft Card Hover |
| `--slate-200` | `#D5E4F5` | 0.7623 | Light Subtle Dividers / Neutral Fill |
| `--slate-300` | `#C7D9EE` | 0.6794 | Clinical Line (Light Borders & Field Outlines) |
| `--slate-400` | `#9BB3D1` | 0.4381 | Dark Mode Secondary Text / Light Disabled Elements |
| `--slate-500` | `#7694B7` | 0.2847 | Dark Mode Muted Caption Text / Accessible Controls |
| `--slate-600` | `#526E8E` | 0.1490 | Light Muted Caption Text / Dark Hover Fill |
| `--slate-700` | `#3D5068` | 0.0773 | Blue-Black (Light Body Text / Dark Elevated Card) |
| `--slate-800` | `#233348` | 0.0319 | Deep Slate / Dark Mode Borders |
| `--slate-850` | `#142032` | 0.0141 | Dark Mode Elevated Container Surface |
| `--slate-900` | `#0E1726` | 0.0085 | Dark Mode Primary Card Surface |
| `--slate-950` | `#0A1220` | 0.0060 | Medical Black (Light Primary Text / High Contrast) |
| `--slate-990` | `#070D18` | 0.0040 | Deep Clinical Void (Dark Mode Canvas Background) |

#### Medical Blue Scale (醫療群青主色階)
| Token | HEX | Luminance | Primary Role |
| :--- | :--- | :--- | :--- |
| `--blue-50` | `#EFF6FF` | 0.9148 | Ice Blue Highlight / Light Active Tint |
| `--blue-100` | `#DEEDFF` | 0.8332 | Accent Soft (Light Badge Background) |
| `--blue-200` | `#BEDBFE` | 0.6877 | Light Focus Outer Glow / Active Chip Border |
| `--blue-300` | `#8EBFF6` | 0.4967 | Dark Mode Badge Text / Link Hover |
| `--blue-400` | `#529DEB` | 0.3191 | Dark Mode Interactive Links / Focus Rings |
| `--blue-500` | `#1D78D6` | 0.1855 | Dark Mode Primary Action Hover |
| `--blue-600` | `#0F6CBD` | 0.1450 | Accent Blue (Dark Mode Primary CTA / Light Active) |
| `--blue-700` | `#064C86` | 0.0693 | Medical Blue (Light Mode Primary CTA Action) |
| `--blue-800` | `#003864` | 0.0375 | Primary Strong (Light Mode CTA Hover & Badge Text) |
| `--blue-900` | `#002646` | 0.0183 | Deep Navy Surface / Dark Mode Badge Background |
| `--blue-950` | `#00162B` | 0.0075 | Midnight Surgical Void |

---

### 2. The 60:30:10 Distribution Rule (色彩空間配置法則)

To maintain a calm, authoritative medical ambiance, interface visual weight is strictly structured into three functional tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│  60% Dominant Neutral (Canvas & Base Surfaces)                         │
│  Light: #F7FAFF / #FFFFFF  |  Dark: #070D18 / #0E1726                 │
│  大面積背景畫布、留白呼吸空間、卡片基底底色                            │
├────────────────────────────────────────────────────────────────────────┤
│  30% Secondary (Content Structure, Typography & Borders)               │
│  Light: #0A1220, #3D5068, #C7D9EE  |  Dark: #F7FAFF, #9BB3D1, #233348 │
│  標題正文、結構分割線、次要卡片外框、標籤容器                          │
├────────────────────────────────────────────────────────────────────────┤
│  10% Accent (Interactive Focus & Highlights)                           │
│  Light: #064C86, #0F6CBD, #DEEDFF  |  Dark: #0F6CBD, #529DEB, #002646  │
│  主要 CTA 按鈕、導航選取狀態、文字連結、焦點光環 (Focus Ring)          │
└────────────────────────────────────────────────────────────────────────┘
```

1. **60% Dominant Neutral (主導底色/畫布)**:
   - 構建全站臨床「通透、沉著」的氛圍基調。
   - 包含全局背景畫布、主容器、模態框底色及大面積負空間（Whitespace）。
   - 禁止在超過 60% 的範圍內使用任何鮮豔色彩。
2. **30% Secondary (結構/排版/邊框)**:
   - 乘載核心醫療與工程資訊，建立清晰的閱讀動線與結構邊界。
   - 包含標題文字（Primary Text）、正文描述（Secondary Copy）、卡片輪廓線（Clinical Line）、輔助背景塊（Subtle Fill）。
3. **10% Accent (焦點/行動呼籲/高亮)**:
   - 精確引導使用者注意力至核心互動點，避免多餘的色彩雜訊。
   - 僅用於關鍵行動按鈕（Primary CTA）、當前頁籤（Active Tab）、超連結（Hyperlink）、鍵盤操作焦點外框（Focus Ring）。

---

### 3. Functional / Semantic Tokens (語意化變數架構)

Design tokens are mapped by function rather than hue, ensuring seamless theme switching between Light and Dark modes.

| Category | Semantic Token | Light Mode Value | Dark Mode Value | Purpose & Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Background (60%)** | `--color-bg-canvas` | `--slate-50` (`#F7FAFF`) | `--slate-990` (`#070D18`) | 全局網頁畫布底色 |
| | `--color-bg-surface` | `#FFFFFF` | `--slate-900` (`#0E1726`) | 卡片、面板、浮動層主要表面 |
| | `--color-bg-surface-elevated` | `#FFFFFF` | `--slate-850` (`#142032`) | 黏性導航、懸浮資訊卡 |
| | `--color-bg-surface-subtle` | `--slate-100` (`#EDF4FC`) | `--slate-850` (`#142032`) | 輸入框底色、次要區塊底色 |
| | `--color-bg-header` | `rgba(255, 255, 255, 0.94)` | `rgba(14, 23, 38, 0.94)` | 頂部導航玻璃模糊底色 |
| **Text (30%)** | `--color-text-primary` | `--slate-950` (`#0A1220`) | `--slate-50` (`#F7FAFF`) | 主要標題、關鍵高對比文字 |
| | `--color-text-secondary` | `--slate-700` (`#3D5068`) | `--slate-400` (`#9BB3D1`) | 正文說明、段落描述、副標題 |
| | `--color-text-muted` | `--slate-600` (`#526E8E`) | `--slate-500` (`#647F9F`) | 輔助說明、日期標註、元數據 |
| | `--color-text-inverse` | `#FFFFFF` | `--slate-950` (`#0A1220`) | 反白文字（深色按鈕或高對比背景） |
| **Border (30%)** | `--color-border-subtle` | `--slate-200` (`#D5E4F5`) | `--slate-800` (`#233348`) | 微弱分割線、清淡外框 |
| | `--color-border-default` | `--slate-300` (`#C7D9EE`) | `--slate-800` (`#233348`) | 標準卡片邊框、輸入框外框 |
| | `--color-border-strong` | `--slate-500` (`#647F9F`) | `--slate-600` (`#526E8E`) | 卡片懸停外框、強調分隔線 |
| **Interactive (10%)** | `--color-action-primary-bg` | `--blue-700` (`#064C86`) | `--blue-600` (`#0F6CBD`) | 主要行動呼籲 (CTA) 按鈕背景 |
| | `--color-action-primary-hover` | `--blue-800` (`#003864`) | `--blue-500` (`#1D78D6`) | 主要按鈕懸停狀態 |
| | `--color-action-primary-text` | `#FFFFFF` | `#FFFFFF` | 主要按鈕內文字 |
| | `--color-action-secondary-border`| `--blue-600` (`#0F6CBD`) | `--blue-400` (`#529DEB`) | 次要外框按鈕邊線 |
| | `--color-action-secondary-text` | `--blue-600` (`#0F6CBD`) | `--blue-400` (`#529DEB`) | 次要按鈕文字顏色 |
| | `--color-link-default` | `--blue-600` (`#0F6CBD`) | `--blue-400` (`#529DEB`) | 內文超連結與強調連結 |
| | `--color-link-hover` | `--blue-700` (`#064C86`) | `--blue-300` (`#8EBFF6`) | 連結懸停色彩 |
| | `--color-badge-bg` | `--blue-100` (`#DEEDFF`) | `--blue-900` (`#002646`) | 標籤徽章背景色 |
| | `--color-badge-text` | `--blue-800` (`#003864`) | `--blue-300` (`#8EBFF6`) | 標籤徽章文字色 |
| | `--color-focus-ring` | `--blue-600` (`#0F6CBD`) | `--blue-400` (`#529DEB`) | 鍵盤導航可訪問性焦點光環 |

---

### 4. WCAG 2.1 Contrast Check (可訪問性對比度驗證)

All combinations strictly satisfy or exceed **WCAG 2.1 Level AA** (minimum 4.5:1 for standard text, 3:1 for large text / UI controls), with key reading text achieving **Level AAA** (minimum 7:1).

#### Light Mode Contrast Check
| UI Element Pairing | Foreground | Background | Contrast Ratio | WCAG Compliance | Evaluation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary Text on Canvas** | `#0A1220` | `#F7FAFF` | **17.92 : 1** | **AAA** (Pass) | 極高清晰度，閱讀無負擔 |
| **Primary Text on Card Surface** | `#0A1220` | `#FFFFFF` | **18.75 : 1** | **AAA** (Pass) | 頂級文字對比度 |
| **Secondary Text on Canvas** | `#3D5068` | `#F7FAFF` | **7.88 : 1** | **AAA** (Pass) | 超越 AAA 標準之臨床次文字 |
| **Secondary Text on Surface** | `#3D5068` | `#FFFFFF` | **8.25 : 1** | **AAA** (Pass) | 優異的正文閱讀性 |
| **Muted Caption Text on Surface** | `#526E8E` | `#FFFFFF` | **5.28 : 1** | **AA** (Pass) | 遠高於 4.5:1 要求 |
| **Primary Button Text in CTA** | `#FFFFFF` | `#064C86` | **8.80 : 1** | **AAA** (Pass) | 醫療藍白按鈕極清晰 |
| **Primary CTA Button on Canvas** | `#064C86` | `#F7FAFF` | **8.41 : 1** | **AAA / UI** (Pass) | 按鈕輪廓遠超 3:1 元件門檻 |
| **Text Link on Canvas** | `#0F6CBD` | `#F7FAFF` | **5.15 : 1** | **AA** (Pass) | 清楚辨識為可點擊連結 |
| **Badge Text on Badge Fill** | `#003864` | `#DEEDFF` | **10.10 : 1** | **AAA** (Pass) | 標籤徽章高對比好讀 |

#### Dark Mode Contrast Check
| UI Element Pairing | Foreground | Background | Contrast Ratio | WCAG Compliance | Evaluation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary Text on Dark Canvas** | `#F7FAFF` | `#070D18` | **18.59 : 1** | **AAA** (Pass) | 深色底高對比主標題 |
| **Primary Text on Dark Surface** | `#F7FAFF` | `#0E1726` | **17.17 : 1** | **AAA** (Pass) | 卡片內主文字無眩光且極度清晰 |
| **Secondary Text on Dark Surface**| `#9BB3D1` | `#0E1726` | **8.35 : 1** | **AAA** (Pass) | 舒適冷藍正文，超越 AAA |
| **Muted Caption Text on Dark** | `#7694B7` | `#0E1726` | **5.72 : 1** | **AA** (Pass) | 遠超 4.5:1 之無眩光輔助文字 |
| **Primary Button Text in CTA** | `#FFFFFF` | `#0F6CBD` | **5.38 : 1** | **AA** (Pass) | 深色模式行動按鈕明亮易讀 |
| **Primary CTA Button on Canvas** | `#0F6CBD` | `#070D18` | **3.61 : 1** | **AA / UI** (Pass) | 滿足 WCAG 1.4.11 元件對比 $\ge 3:1$ |
| **Dark Link on Dark Surface** | `#529DEB` | `#0E1726` | **6.31 : 1** | **AA** (Pass) | 視覺穿透力強的冷藍超連結 |
| **Dark Badge Text on Badge Fill** | `#8EBFF6` | `#002646` | **8.01 : 1** | **AAA** (Pass) | 深藍底淺藍字極清晰 |

---

### 5. Dark Mode Design Specifications (深色模式設計規範)

1. **Avoid Pure Black `#000000`**:
   - 嚴禁使用全黑底色。採用帶有幽微冷藍質感的醫療深色色階（Canvas: `#070D18`、Card Surface: `#0E1726`、Elevated Container: `#142032`）。
   - 保留冷色調深度，維持臨床理性的品牌調性，同時避免 OLED 螢幕上的像素拖影與極端黑白對比引發的視覺疲勞。
2. **Layered Elevation via Lightness (階梯式亮度分層)**:
   - 淺色模式依賴陰影與邊線界定層級；深色模式則透過微幅提升表面亮度（Surface Luminance）來展現海拔高度（Elevation）：
     `Canvas (#070D18)` $\rightarrow$ `Base Card (#0E1726)` $\rightarrow$ `Elevated / Header (#142032)`。
3. **Desaturated & Shifted Accents (飽和度微調)**:
   - 避免直接將淺色模式的高飽和深藍（`#064C86`）置於深黑背景上，以免產生色彩振動（Chromostereopsis）。深色模式將互動色階往上提升至 `--blue-400` (`#529DEB`) 與 `--blue-600` (`#0F6CBD`)，確保清澈透亮。
4. **Implementation Support**:
   - 支援系統偏好 `@media (prefers-color-scheme: dark)` 與手動指定 `[data-theme="dark"]` / `[data-theme="light"]`。


## Typography and components

- Use Inter with Noto Sans TC fallback for body copy, and Lexend for compact display hierarchy.
- Buttons are at least 44px tall, in medical blue or a blue outline.
- Cards use white surfaces, a 1px clinical-blue border, and a restrained shadow.
- Inputs have labels above, a white field, and a blue focus ring.
- Icons are Animate UI open-source icon shapes with small, optional motion; reduced-motion preferences disable it.

## Layout and interaction

Use a maximum 1200px grid with generous padding. Prefer asymmetric two-column layouts for editorial sections and collapse columns on narrow screens. Avoid generic equal-card grids when a clearer hierarchy exists.

Motion is limited to small hover and menu feedback. No custom cursors, overlap, fake metrics, decorative imagery, or athletic visual language.
