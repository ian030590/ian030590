(() => {
  "use strict";

  const githubUser = "ian030590";
  const experience = [
    {
      period: "2025/1 至今",
      title: "研究助理",
      org: "社團法人台灣視覺復健專業服務協會",
      description:
        "負責勞動部研究計畫申請與報告撰寫、研究收案、視覺評估、視覺復健、研究行政與資料處理；並以 AI 建置及維護門診病歷與研究個案紀錄系統。",
    },
    {
      period: "2023/9 至 2024/12",
      title: "專任研究助理",
      org: "臺北市立聯合醫院",
      description:
        "執行內分泌與新陳代謝科及眼科部研究收案，協助國科會研究行政、研究倫理申請、個案管理，以及視覺評估與視覺復健。",
    },
    {
      period: "2025/2 至 2026/12｜就讀中",
      title: "職能治療學系 碩士",
      org: "國立臺灣大學",
      description:
        "研究聚焦於視覺功能評估、視覺復能與臨床研究，探討雙眼視覺功能、深度知覺與眼球動作特徵。",
    },
    {
      period: "2019/9 至 2023/6｜畢業",
      title: "職能治療學系 學士",
      org: "國立臺灣大學",
      description:
        "建立職能治療臨床推理、視覺復健與跨專業協作的基礎，並延伸投入臨床研究與數位健康工具開發。",
    },
  ];

  const escapeHtml = (value) =>
    String(value ?? "").replace(
      /[&<>"']/g,
      (char) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[char],
    );

  const renderTags = (value) =>
    String(value || "")
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean)
      .map(
        (tag, index) =>
          `<span class="tag ${index % 2 ? "blue" : ""}">${escapeHtml(tag)}</span>`,
      )
      .join("");

  // Theme Management (Light / Dark Mode with System Preference Fallback)
  const getInitialTheme = () => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark" || savedTheme === "light") {
      return savedTheme;
    }
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  };

  const applyTheme = (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
    document.querySelectorAll(".theme-toggle").forEach((btn) => {
      const darkIcon = btn.querySelector(".icon-dark");
      const lightIcon = btn.querySelector(".icon-light");
      if (darkIcon && lightIcon) {
        darkIcon.style.display = theme === "dark" ? "none" : "inline-block";
        lightIcon.style.display = theme === "dark" ? "inline-block" : "none";
      }
      btn.setAttribute("aria-label", theme === "dark" ? "切換至淺色模式" : "切換至深色模式");
      btn.setAttribute("title", theme === "dark" ? "切換至淺色模式" : "切換至深色模式");
    });
  };

  const initialTheme = getInitialTheme();
  applyTheme(initialTheme);

  document.querySelectorAll(".theme-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const currentTheme =
        document.documentElement.getAttribute("data-theme") || getInitialTheme();
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      localStorage.setItem("theme", nextTheme);
      applyTheme(nextTheme);
    });
  });

  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!localStorage.getItem("theme")) {
        applyTheme(e.matches ? "dark" : "light");
      }
    });
  }

  document.querySelectorAll("[data-year]").forEach((node) => {
    node.textContent = new Date().getFullYear();
  });

  const menu = document.querySelector(".menu-button");
  const mobilePanel = document.querySelector(".mobile-panel");
  if (menu && mobilePanel) {
    menu.addEventListener("click", () => {
      const open = mobilePanel.classList.toggle("open");
      menu.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("is-open", open);
    });
  }

  const experienceList = document.getElementById("experience-list");
  if (experienceList) {
    experienceList.innerHTML = experience
      .map(
        (item) => `
      <article class="timeline-item">
        <div class="timeline-period">${escapeHtml(item.period)}</div>
        <h3>${escapeHtml(item.title)}</h3>
        <div class="timeline-org">${escapeHtml(item.org)}</div>
        <p>${escapeHtml(item.description)}</p>
      </article>
    `,
      )
      .join("");
  }

  // 自訂專案預覽圖對照表（若儲存庫有特定圖片或截圖可在此指定，否則預設使用 GitHub 官方 Social Preview 圖片）
  const customProjectPreviews = {
    // 例如："VisionTrainer": "./assets/projects/vision-trainer.png",
  };

  const getProjectPreview = (repo) => {
    if (customProjectPreviews[repo.name]) {
      return customProjectPreviews[repo.name];
    }
    // GitHub 官方 OpenGraph 社群預覽圖片 (1200x630)
    // 若在 GitHub 儲存庫設定中有上傳 Social Preview，將自動使用該自訂圖；若無則自動生成帶有專案資訊的預覽圖
    return `https://opengraph.githubassets.com/1/${githubUser}/${repo.name}`;
  };

  const projectsGrid = document.getElementById("projects-grid");
  if (projectsGrid) {
    fetch(
      `https://api.github.com/users/${githubUser}/repos?sort=updated&direction=desc&per_page=100`,
    )
      .then((response) => {
        if (!response.ok) throw new Error("GitHub API request failed");
        return response.json();
      })
      .then((repositories) => {
        // 排除特殊個人 Profile README 儲存庫、本作品集網站自身以及 Fork 專案
        const excludedRepos = [githubUser.toLowerCase(), "myportfolio"];
        const displayRepos = repositories.filter(
          (repo) =>
            !excludedRepos.includes(repo.name.toLowerCase()) && !repo.fork,
        );
        const targetList = displayRepos.length ? displayRepos : repositories;

        if (!targetList.length) {
          projectsGrid.innerHTML =
            '<div class="empty-state"><p>尚無公開開源專案。</p></div>';
          return;
        }

        projectsGrid.innerHTML = targetList
          .map((repo) => {
            const topics = Array.isArray(repo.topics) ? repo.topics : [];
            const labels = [repo.language, ...topics]
              .filter(Boolean)
              .slice(0, 4)
              .join(", ");
            const description =
              repo.description || `由 ${githubUser} 開發的開源專案。`;
            const previewUrl = getProjectPreview(repo);
            const updatedDate = new Date(repo.updated_at).toLocaleDateString(
              "zh-TW",
              {
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
              },
            );

            return `
              <article class="project-card">
                <a class="card-link" href="${escapeHtml(repo.html_url)}" target="_blank" rel="noopener">
                  <div class="project-visual">
                    <img
                      src="${escapeHtml(previewUrl)}"
                      alt="${escapeHtml(repo.name)} 專案預覽圖"
                      loading="lazy"
                      onerror="this.parentElement.classList.add('no-image'); this.remove();"
                    />
                    <div class="project-visual-placeholder">
                      <div class="github-mark">
                        <span class="material-symbols-outlined">code</span>
                      </div>
                    </div>
                  </div>
                  <div class="project-content">
                    <div class="tags">${renderTags(labels)}</div>
                    <h2>${escapeHtml(repo.name)}</h2>
                    <p>${escapeHtml(description)}</p>
                    <div class="project-footer">
                      <span class="section-kicker">更新於 ${escapeHtml(updatedDate)}</span>
                      <div class="project-footer-right">
                        ${
                          repo.stargazers_count > 0
                            ? `<span class="project-stars" title="${repo.stargazers_count} 個星標">
                                <span class="material-symbols-outlined star-icon" aria-hidden="true">star</span>
                                ${repo.stargazers_count}
                              </span>`
                            : ""
                        }
                        <span class="text-link">
                          View on GitHub
                          <span class="material-symbols-outlined">open_in_new</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </a>
              </article>
            `;
          })
          .join("");
      })
      .catch(() => {
        projectsGrid.innerHTML = `
          <div class="empty-state">
            <span class="material-symbols-outlined" style="font-size: 38px; color: var(--muted); margin-bottom: 8px;">cloud_off</span>
            <p>暫時無法載入 GitHub 專案列表，請稍候再試。</p>
          </div>
        `;
      });
  }

  const articleContent = document.getElementById("article-content");
  const tagsFilterList = document.getElementById("tags-filter-list");
  const tagsCountBadge = document.getElementById("tags-count-badge");
  const filterStatusBar = document.getElementById("filter-status-bar");
  const activeFilterName = document.getElementById("active-filter-name");
  const activeFilterCount = document.getElementById("active-filter-count");
  const clearFilterBtn = document.getElementById("clear-filter-btn");
  const blogSearchInput = document.getElementById("blog-search");
  const clearSearchBtn = document.getElementById("clear-search-btn");

  if (articleContent) {
    let allPosts = [];
    let currentTag = "ALL";
    let searchQuery = "";

    // Read initial tag from URL if present
    const urlParams = new URLSearchParams(window.location.search);
    const initialTag = urlParams.get("tag");
    if (initialTag) {
      currentTag = initialTag;
    }

    const plainText = (value) => {
      const box = document.createElement("div");
      box.innerHTML = value || "";
      return (box.textContent || "").replace(/\s+/g, " ").trim();
    };

    const extractImage = (html, mediaThumb) => {
      // 1. Try to find <img> tag in HTML
      const imgMatch = (html || "").match(/<img[^>]+src=["']([^"']+)["']/i);
      if (imgMatch && imgMatch[1]) {
        let src = imgMatch[1];
        if (src.startsWith("//")) src = "https:" + src;
        return src;
      }
      // 2. Try media$thumbnail with resolution upscaled
      if (mediaThumb) {
        let src = mediaThumb;
        if (src.startsWith("//")) src = "https:" + src;
        src = src.replace(/\/s72-c(-[^/]+)?\//i, "/s1600/");
        src = src.replace(/\/w72-h72(-[^/]+)?\//i, "/w1200-h630-c/");
        return src;
      }
      return "";
    };

    const extractExcerpt = (html) => {
      // Priority 1: <header> <p> which contains the curated executive summary in the articles
      const headerPMatch = (html || "").match(
        /<header[\s\S]*?<p[^>]*>([\s\S]*?)<\/p>/i,
      );
      if (headerPMatch && headerPMatch[1]) {
        const text = plainText(headerPMatch[1]);
        if (text.length > 10) return text;
      }
      // Priority 2: first <p> in article body
      const pMatch = (html || "").match(/<p[^>]*>([\s\S]*?)<\/p>/i);
      if (pMatch && pMatch[1]) {
        const text = plainText(pMatch[1]);
        if (text.length > 10) return text.slice(0, 160);
      }
      // Priority 3: clean text
      return plainText(html).slice(0, 150);
    };

    const extractReadingTime = (html, fullText) => {
      const match = (html || "").match(/閱讀時間[：:]\s*([0-9]+)\s*分鐘/);
      if (match && match[1]) {
        return `約 ${match[1]} 分鐘閱讀`;
      }
      const charCount = fullText.length;
      const minutes = Math.max(3, Math.ceil(charCount / 380));
      return `約 ${minutes} 分鐘閱讀`;
    };

    const updateURL = () => {
      const url = new URL(window.location.href);
      if (currentTag && currentTag !== "ALL") {
        url.searchParams.set("tag", currentTag);
      } else {
        url.searchParams.delete("tag");
      }
      window.history.replaceState({}, "", url.toString());
    };

    const renderArticles = () => {
      const filtered = allPosts.filter((post) => {
        const matchesTag =
          currentTag === "ALL" || post.tags.includes(currentTag);
        if (!matchesTag) return false;

        if (!searchQuery) return true;
        const q = searchQuery.toLowerCase();
        return (
          post.title.toLowerCase().includes(q) ||
          post.lead.toLowerCase().includes(q) ||
          post.tags.some((t) => t.toLowerCase().includes(q))
        );
      });

      // Update Filter Status Bar
      const isFiltered = currentTag !== "ALL" || searchQuery.length > 0;
      if (filterStatusBar) {
        if (isFiltered) {
          filterStatusBar.style.display = "flex";
          let labelText = "";
          if (currentTag !== "ALL" && searchQuery) {
            labelText = `標籤「${currentTag}」+ 關鍵字「${searchQuery}」`;
          } else if (currentTag !== "ALL") {
            labelText = `主題標籤「${currentTag}」`;
          } else {
            labelText = `搜尋關鍵字「${searchQuery}」`;
          }
          if (activeFilterName) activeFilterName.textContent = labelText;
          if (activeFilterCount)
            activeFilterCount.textContent = `(${filtered.length} 篇)`;
        } else {
          filterStatusBar.style.display = "none";
        }
      }

      // Update Active Tag Button in Sidebar
      if (tagsFilterList) {
        tagsFilterList.querySelectorAll(".tag-filter-btn").forEach((btn) => {
          const btnTag = btn.getAttribute("data-tag");
          btn.classList.toggle("active", btnTag === currentTag);
        });
      }

      if (!filtered.length) {
        articleContent.innerHTML = `
          <div class="empty-state">
            <span class="material-symbols-outlined" style="font-size: 40px; color: var(--muted); margin-bottom: 12px;">search_off</span>
            <p>沒有找到符合條件的文章。</p>
            <button class="button-secondary reset-filter-btn" type="button" style="margin-top: 14px;">
              清除篩選條件
            </button>
          </div>
        `;
        const resetBtn = articleContent.querySelector(".reset-filter-btn");
        if (resetBtn) {
          resetBtn.addEventListener("click", () => {
            currentTag = "ALL";
            searchQuery = "";
            if (blogSearchInput) blogSearchInput.value = "";
            if (clearSearchBtn) clearSearchBtn.style.display = "none";
            updateURL();
            renderArticles();
          });
        }
        return;
      }

      // Determine if we should show featured layout for post 0
      const showFeatured =
        currentTag === "ALL" && !searchQuery && filtered.length > 1;

      const articlesHtml = filtered
        .map((post, index) => {
          const isFeatured = showFeatured && index === 0;

          // Render interactive tags inside cards
          const tagsMarkup = post.tags
            .map(
              (tag, tagIdx) =>
                `<button type="button" class="card-tag-pill ${tagIdx % 2 ? "blue" : ""}" data-card-tag="${escapeHtml(tag)}">${escapeHtml(tag)}</button>`,
            )
            .join("");

          const imageMarkup = post.imageUrl
            ? `<div class="article-visual">
                <img src="${escapeHtml(post.imageUrl)}" alt="${escapeHtml(post.title)}" loading="lazy" onerror="this.parentElement.classList.add('no-image'); this.remove();" />
                ${isFeatured ? '<span class="featured-badge"><span class="material-symbols-outlined" style="font-size: 14px;">star</span>最新專題</span>' : ""}
              </div>`
            : `<div class="article-visual no-image">
                <div class="article-visual-placeholder">
                  <span class="material-symbols-outlined">article</span>
                </div>
                ${isFeatured ? '<span class="featured-badge"><span class="material-symbols-outlined" style="font-size: 14px;">star</span>最新專題</span>' : ""}
              </div>`;

          return `
            <article class="article-card ${isFeatured ? "article-card--featured" : ""}">
              <a class="card-link" href="${escapeHtml(post.link)}" target="_blank" rel="noopener">
                ${imageMarkup}
                <div class="article-content">
                  <div class="card-tags-row">${tagsMarkup}</div>
                  <h2 class="article-title">${escapeHtml(post.title)}</h2>
                  <div class="article-meta">
                    <span class="meta-item">
                      <span class="material-symbols-outlined" aria-hidden="true">calendar_today</span>
                      ${escapeHtml(post.dateString)}
                    </span>
                    <span class="meta-item">
                      <span class="material-symbols-outlined" aria-hidden="true">schedule</span>
                      ${escapeHtml(post.readTime)}
                    </span>
                  </div>
                  <p class="article-excerpt">${escapeHtml(post.lead)}</p>
                  <div class="article-footer">
                    <span class="source-kicker">${escapeHtml(post.sourceName || "Blogger")}</span>
                    <span class="read-more-link">
                      閱讀全文
                      <span class="material-symbols-outlined" aria-hidden="true">arrow_forward</span>
                    </span>
                  </div>
                </div>
              </a>
            </article>
          `;
        })
        .join("");

      articleContent.innerHTML = `<div class="articles-grid">${articlesHtml}</div>`;

      // Attach click listeners to tags on article cards
      articleContent.querySelectorAll("[data-card-tag]").forEach((tagBtn) => {
        tagBtn.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          const selectedTag = tagBtn.getAttribute("data-card-tag");
          if (selectedTag) {
            currentTag = selectedTag;
            updateURL();
            renderArticles();
            if (window.innerWidth <= 960) {
              const top =
                articleContent.getBoundingClientRect().top +
                window.scrollY -
                90;
              window.scrollTo({ top, behavior: "smooth" });
            }
          }
        });
      });
    };

    const renderSidebarTags = (tagCounts) => {
      if (!tagsFilterList) return;

      const sortedTags = Object.keys(tagCounts).sort((a, b) => {
        const diff = tagCounts[b] - tagCounts[a];
        return diff !== 0 ? diff : a.localeCompare(b, "zh-Hant");
      });

      if (tagsCountBadge) {
        tagsCountBadge.textContent = `${sortedTags.length} 個標籤`;
      }

      const allBtnHtml = `
        <button type="button" class="tag-filter-btn ${currentTag === "ALL" ? "active" : ""}" data-tag="ALL">
          <span class="tag-name">全部文章</span>
          <span class="tag-count">${allPosts.length}</span>
        </button>
      `;

      const tagsHtml = sortedTags
        .map((tag) => {
          const count = tagCounts[tag];
          const isActive = currentTag === tag;
          return `
            <button type="button" class="tag-filter-btn ${isActive ? "active" : ""}" data-tag="${escapeHtml(tag)}">
              <span class="tag-name">${escapeHtml(tag)}</span>
              <span class="tag-count">${count}</span>
            </button>
          `;
        })
        .join("");

      tagsFilterList.innerHTML = allBtnHtml + tagsHtml;

      tagsFilterList.querySelectorAll(".tag-filter-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          const tag = btn.getAttribute("data-tag") || "ALL";
          currentTag = tag;
          updateURL();
          renderArticles();
        });
      });
    };

    // Setup clear filter button
    if (clearFilterBtn) {
      clearFilterBtn.addEventListener("click", () => {
        currentTag = "ALL";
        searchQuery = "";
        if (blogSearchInput) blogSearchInput.value = "";
        if (clearSearchBtn) clearSearchBtn.style.display = "none";
        updateURL();
        renderArticles();
      });
    }

    // Setup live search
    if (blogSearchInput) {
      blogSearchInput.addEventListener("input", (e) => {
        searchQuery = (e.target.value || "").trim();
        if (clearSearchBtn) {
          clearSearchBtn.style.display = searchQuery ? "flex" : "none";
        }
        renderArticles();
      });
    }

    if (clearSearchBtn) {
      clearSearchBtn.addEventListener("click", () => {
        if (blogSearchInput) blogSearchInput.value = "";
        searchQuery = "";
        clearSearchBtn.style.display = "none";
        renderArticles();
      });
    }

    const blogSources = [
      {
        id: "4355302929541717814",
        name: "職能治療日誌",
        feedUrl: "https://www.blogger.com/feeds/4355302929541717814/posts/default",
        siteUrl: "https://ian030590ot.blogspot.com",
        defaultTags: ["職能治療", "臨床復健"],
      },
      {
        id: "1728297252870027743",
        name: "數位學習日誌",
        feedUrl: "https://ian030590digital.blogspot.com/feeds/posts/default",
        siteUrl: "https://ian030590digital.blogspot.com",
        defaultTags: ["臨床筆記", "數位健康"],
      },
    ];

    const parseEntry = (entry, source) => {
      const html = entry.content?.$t || entry.summary?.$t || "";
      const rawText = plainText(html);

      // Title: direct title or fallback to <h1>/<h2>/<title> in HTML
      const directTitle = (entry.title?.$t || "").trim();
      let title = directTitle;
      if (!title) {
        const hMatch =
          html.match(/<h[12][^>]*>([\s\S]*?)<\/h[12]>/i) ||
          html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
        title = hMatch ? plainText(hMatch[1]) : "專業文章";
      }

      // Image
      const mediaThumb = entry.media$thumbnail?.url;
      const imageUrl = extractImage(html, mediaThumb);

      // Excerpt / Lead
      const lead = extractExcerpt(html);

      // Tags: check Blogger categories, then HTML inline (視角/主題), then source defaults
      let tags = (entry.category || [])
        .map((c) => (c.term || "").trim())
        .filter(Boolean);

      if (!tags.length && html) {
        const customTags = [];
        const matches = html.matchAll(/(?:視角|主題)[：:]([^<]+)/g);
        for (const m of matches) {
          const t = plainText(m[1]).trim();
          if (t && !customTags.includes(t)) {
            customTags.push(t);
          }
        }
        if (customTags.length) {
          tags = customTags;
        }
      }

      if (source.name === "職能治療日誌" && !tags.includes("職能治療")) {
        tags.unshift("職能治療");
      }

      if (!tags.length) {
        tags = source.defaultTags
          ? [...source.defaultTags]
          : ["臨床筆記", "專業文章"];
      }

      // Date
      const dateObj = entry.published?.$t
        ? new Date(entry.published.$t)
        : null;
      const dateString = dateObj
        ? dateObj.toLocaleDateString("zh-TW", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
        : "";

      // Read time
      const readTime = extractReadingTime(html, rawText);

      // Link
      const link =
        entry.link?.find((item) => item.rel === "alternate")?.href ||
        source.siteUrl;

      return {
        id: entry.id?.$t || `${source.id}-${Math.random()}`,
        title,
        lead,
        imageUrl,
        tags,
        dateObj,
        dateString,
        readTime,
        link,
        sourceName: source.name,
      };
    };

    const fetchBloggerFeed = (source, timeoutMs = 10000) => {
      return new Promise((resolve) => {
        const cbName = `__handleBlogger_${source.id}_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
        let timer = null;

        const cleanup = () => {
          if (timer) {
            clearTimeout(timer);
            timer = null;
          }
          try {
            delete window[cbName];
          } catch (_) {
            window[cbName] = undefined;
          }
          const s = document.getElementById(`blogger-script-${source.id}`);
          if (s) s.remove();
        };

        timer = setTimeout(() => {
          cleanup();
          resolve([]);
        }, timeoutMs);

        window[cbName] = (feed) => {
          cleanup();
          const entries = feed?.feed?.entry || [];
          const posts = entries.map((entry) => parseEntry(entry, source));
          resolve(posts);
        };

        const script = document.createElement("script");
        script.id = `blogger-script-${source.id}`;
        script.src = `${source.feedUrl}?alt=json-in-script&callback=${cbName}&max-results=50`;
        script.async = true;
        script.onerror = () => {
          cleanup();
          resolve([]);
        };

        document.head.appendChild(script);
      });
    };

    Promise.all(blogSources.map((source) => fetchBloggerFeed(source))).then(
      (results) => {
        allPosts = results.flat();
        if (!allPosts.length) {
          articleContent.innerHTML =
            '<div class="empty-state">目前尚無公開文章或文章暫時無法載入，請稍候再試。</div>';
          if (tagsFilterList) tagsFilterList.innerHTML = "";
          return;
        }

        // Sort chronologically descending (newest first)
        allPosts.sort((a, b) => {
          const timeA = a.dateObj ? a.dateObj.getTime() : 0;
          const timeB = b.dateObj ? b.dateObj.getTime() : 0;
          return timeB - timeA;
        });

        // Tally tag counts
        const tagCounts = {};
        allPosts.forEach((post) => {
          post.tags.forEach((t) => {
            tagCounts[t] = (tagCounts[t] || 0) + 1;
          });
        });

        renderSidebarTags(tagCounts);
        renderArticles();
      },
    );
  }

  const contactForm = document.getElementById("contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(contactForm);
      const subject = data.get("subject");
      const name = data.get("name");
      const body = data.get("body");
      window.location.href = `mailto:rainbowh9490@gmail.com?subject=${encodeURIComponent(`[Website Contact] ${subject} - ${name}`)}&body=${encodeURIComponent(`From: ${name}\n\n${body}`)}`;
    });
  }
})();
