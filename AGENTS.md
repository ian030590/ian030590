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
