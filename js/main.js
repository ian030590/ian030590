<<<<<<< HEAD
(() => {
  "use strict";

  const githubUser = "ian030590";

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

  // Storage can throw in private windows or with site data blocked.
  const readTheme = () => {
    try {
      return localStorage.getItem("theme");
    } catch (error) {
      return null;
    }
  };
  const saveTheme = (theme) => {
    try {
      localStorage.setItem("theme", theme);
    } catch (error) {
      // The toggle still works for this page view.
    }
  };

  const prefersDark = () =>
    Boolean(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);

  const getInitialTheme = () => {
    const savedTheme = readTheme();
    if (savedTheme === "dark" || savedTheme === "light") return savedTheme;
    return prefersDark() ? "dark" : "light";
  };

  const applyTheme = (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
    const label = theme === "dark" ? "切換至淺色模式" : "切換至深色模式";
    document.querySelectorAll(".theme-toggle").forEach((btn) => {
      const darkIcon = btn.querySelector(".icon-dark");
      const lightIcon = btn.querySelector(".icon-light");
      if (darkIcon && lightIcon) {
        darkIcon.style.display = theme === "dark" ? "none" : "inline-block";
        lightIcon.style.display = theme === "dark" ? "inline-block" : "none";
      }
      btn.setAttribute("aria-label", label);
      btn.setAttribute("title", label);
    });
  };

  applyTheme(getInitialTheme());

  document.querySelectorAll(".theme-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const currentTheme =
        document.documentElement.getAttribute("data-theme") || getInitialTheme();
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      saveTheme(nextTheme);
      applyTheme(nextTheme);
    });
  });

  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!readTheme()) applyTheme(e.matches ? "dark" : "light");
    });
  }

  document.querySelectorAll("[data-year]").forEach((node) => {
    node.textContent = new Date().getFullYear();
  });

  const menu = document.querySelector(".menu-button");
  const mobilePanel = document.querySelector(".mobile-panel");
  if (menu && mobilePanel) {
    const setMenu = (open) => {
      mobilePanel.classList.toggle("open", open);
      menu.classList.toggle("is-open", open);
      menu.setAttribute("aria-expanded", String(open));
      menu.setAttribute("aria-label", open ? "關閉選單" : "開啟選單");
    };
    menu.addEventListener("click", () => {
      setMenu(!mobilePanel.classList.contains("open"));
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && mobilePanel.classList.contains("open")) {
        setMenu(false);
        menu.focus();
      }
    });
  }

  const projectsGrid = document.getElementById("projects-grid");
  if (projectsGrid) {
    const projectsStatus = document.getElementById("projects-status");
    const snapshot = window.GITHUB_PROJECTS || { repositories: [] };
    const excludedRepos = [githubUser.toLowerCase(), "myportfolio"];

    const renderProjects = (repositories) => {
      if (!Array.isArray(repositories)) throw new Error("Invalid project list");
      const targetList = repositories.filter(
        (repo) =>
          !excludedRepos.includes(repo.name.toLowerCase()) && !repo.fork && !repo.private,
      );

      if (!targetList.length) {
        projectsGrid.innerHTML = '<p class="empty-state">尚無公開開源專案。</p>';
        return;
      }

      projectsGrid.innerHTML = targetList
        .map((repo) => {
          const topics = Array.isArray(repo.topics) ? repo.topics : [];
          const labels = [repo.archived ? "已封存" : null, repo.language, ...topics]
            .filter(Boolean)
            .slice(0, 4);
          // GitHub renders a 1200×630 preview per repository, or the uploaded social preview.
          const previewUrl = `https://opengraph.githubassets.com/1/${githubUser}/${repo.name}`;
          const updatedDate = new Date(repo.updated_at).toLocaleDateString("zh-TW", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          });
          const stars =
            repo.stargazers_count > 0
              ? `<span class="project-stars" title="${repo.stargazers_count} 個 GitHub 星號">
                  <span class="material-symbols-outlined" aria-hidden="true">star</span>
                  ${repo.stargazers_count}
                </span>`
              : "";

          return `
            <article class="project-card">
              <a class="card-link" href="${escapeHtml(repo.html_url)}" target="_blank" rel="noopener">
                <div class="project-visual">
                  <img
                    src="${escapeHtml(previewUrl)}"
                    alt=""
                    loading="lazy"
                    onerror="this.remove();"
                  />
                </div>
                <div class="project-content">
                  <div class="tags">${labels.map((label) => `<span class="tag">${escapeHtml(label)}</span>`).join("")}</div>
                  <h2>${escapeHtml(repo.name)}</h2>
                  ${repo.description ? `<p>${escapeHtml(repo.description)}</p>` : ""}
                  <div class="project-footer">
                    <span class="project-updated">更新於 ${escapeHtml(updatedDate)}</span>
                    <span class="project-footer-right">
                      ${stars}
                      <span class="text-link">在 GitHub 查看</span>
                    </span>
                  </div>
                </div>
              </a>
            </article>
          `;
        })
        .join("");
    };

    if (snapshot.repositories.length) {
      renderProjects(snapshot.repositories);
      if (projectsStatus) {
        projectsStatus.textContent = `目前顯示 ${snapshot.synced_at} 整理的公開專案，正在取得最新清單。`;
      }
    }

    fetch(
      `https://api.github.com/users/${githubUser}/repos?type=owner&sort=updated&direction=desc&per_page=100`,
    )
      .then((response) => {
        if (!response.ok) throw new Error("GitHub API request failed");
        return response.json();
      })
      .then((repositories) => {
        renderProjects(repositories);
        if (projectsStatus) projectsStatus.textContent = "已同步 GitHub 最新公開專案；已封存作品以標籤註明。";
      })
      .catch(() => {
        if (snapshot.repositories.length) {
          if (projectsStatus) projectsStatus.textContent = `目前顯示 ${snapshot.synced_at} 整理的公開專案；最新動態請見各專案的 GitHub 頁面。`;
          return;
        }
        if (projectsStatus) projectsStatus.textContent = "專案清單暫時無法更新。";
        projectsGrid.innerHTML = `
          <div class="empty-state">
            <p>GitHub 暫時沒有回應，請<a href="https://github.com/${githubUser}?tab=repositories" target="_blank" rel="noopener noreferrer">前往 GitHub 查看公開專案</a>。</p>
          </div>
        `;
      });
  }

  const articleContent = document.getElementById("article-content");
  const tagsFilterList = document.getElementById("tags-filter-list");
  const filterStatusBar = document.getElementById("filter-status-bar");
  const activeFilterName = document.getElementById("active-filter-name");
  const activeFilterCount = document.getElementById("active-filter-count");
  const clearFilterBtn = document.getElementById("clear-filter-btn");
  const blogSearchInput = document.getElementById("blog-search");
  const clearSearchBtn = document.getElementById("clear-search-btn");

  if (articleContent) {
    const articlesPerPage = 15;
    let allPosts = [];
    let currentTag = new URLSearchParams(window.location.search).get("tag") || "ALL";
    let searchQuery = "";

    const updateURL = () => {
      const url = new URL(window.location.href);
      if (currentTag && currentTag !== "ALL") {
        url.searchParams.set("tag", currentTag);
      } else {
        url.searchParams.delete("tag");
      }
      window.history.replaceState({}, "", url.toString());
    };

    const resetFilters = () => {
      currentTag = "ALL";
      searchQuery = "";
      if (blogSearchInput) blogSearchInput.value = "";
      if (clearSearchBtn) clearSearchBtn.hidden = true;
      updateURL();
      renderArticles();
    };

    const describeFilter = () => {
      if (currentTag !== "ALL" && searchQuery) return `標籤「${currentTag}」與關鍵字「${searchQuery}」`;
      if (currentTag !== "ALL") return `標籤「${currentTag}」`;
      return `關鍵字「${searchQuery}」`;
    };

    const renderArticles = (page = 1) => {
      const q = searchQuery.toLowerCase();
      const filtered = allPosts.filter((post) => {
        if (currentTag !== "ALL" && !post.tags.includes(currentTag)) return false;
        if (!q) return true;
        return (
          post.title.toLowerCase().includes(q) ||
          post.lead.toLowerCase().includes(q) ||
          post.tags.some((t) => t.toLowerCase().includes(q))
        );
      });

      const isFiltered = currentTag !== "ALL" || searchQuery.length > 0;
      if (filterStatusBar) {
        filterStatusBar.hidden = !isFiltered;
        if (isFiltered) {
          if (activeFilterName) activeFilterName.textContent = describeFilter();
          if (activeFilterCount) activeFilterCount.textContent = `(${filtered.length} 篇)`;
        }
      }

      if (tagsFilterList) {
        tagsFilterList.querySelectorAll(".tag-filter-btn").forEach((btn) => {
          const isActive = btn.getAttribute("data-tag") === currentTag;
          btn.classList.toggle("active", isActive);
          btn.setAttribute("aria-pressed", String(isActive));
        });
      }

      if (!filtered.length) {
        articleContent.innerHTML = `
          <div class="empty-state">
            <p>沒有符合${escapeHtml(describeFilter())}的文章。搜尋範圍是標題、摘要與標籤。</p>
            <button class="button-secondary reset-filter-btn" type="button">清除篩選條件</button>
          </div>
        `;
        articleContent.querySelector(".reset-filter-btn").addEventListener("click", resetFilters);
        return;
      }

      const showFeatured =
        currentTag === "ALL" && !searchQuery && page === 1 && filtered.length > 1;
      const totalPages = Math.max(1, Math.ceil(filtered.length / articlesPerPage));
      const currentPage = Math.max(1, Math.min(page, totalPages));
      const startIndex = (currentPage - 1) * articlesPerPage;
      const pagePosts = filtered.slice(startIndex, startIndex + articlesPerPage);

      const articlesHtml = pagePosts
        .map((post, index) => {
          const isFeatured = showFeatured && index === 0;
          const badge = isFeatured ? '<span class="featured-badge">最新專題</span>' : "";
          const tagsMarkup = post.tags
            .map((tag) => `<span class="card-tag-pill">${escapeHtml(tag)}</span>`)
            .join("");
          const imageMarkup = post.imageUrl
            ? `<div class="article-visual">
                <img src="${escapeHtml(post.imageUrl)}" alt="" loading="lazy" onerror="this.parentElement.classList.add('no-image'); this.remove();" />
                ${badge}
              </div>`
            : `<div class="article-visual no-image">${badge}</div>`;

          return `
            <article class="article-card ${isFeatured ? "article-card--featured" : ""}">
              <a class="card-link" href="${escapeHtml(post.link)}">
                ${imageMarkup}
                <div class="article-content">
                  <div class="card-tags-row">${tagsMarkup}</div>
                  <h2 class="article-title">${escapeHtml(post.title)}</h2>
                  <div class="article-meta">
                    <time datetime="${escapeHtml(post.dateString)}">${escapeHtml(post.dateString)}</time>
                    <span>${escapeHtml(post.readTime)}</span>
                  </div>
                  <p class="article-excerpt">${escapeHtml(post.lead)}</p>
                  <div class="article-footer">
                    <span class="source-kicker">${escapeHtml(post.category)}</span>
                    <span class="read-more-link">閱讀全文</span>
                  </div>
                </div>
              </a>
            </article>
          `;
        })
        .join("");

      const paginationHtml = `
        <nav class="article-pagination" aria-label="文章分頁">
          <p class="article-page-status" role="status">第 ${startIndex + 1} 至 ${startIndex + pagePosts.length} 篇，共 ${filtered.length} 篇</p>
          ${totalPages > 1 ? `
            <div class="pagination-controls">
              <button type="button" class="pagination-button" data-page="${currentPage - 1}" ${currentPage === 1 ? "disabled" : ""}>上一頁</button>
              ${Array.from({ length: totalPages }, (_, index) => {
                const number = index + 1;
                return `<button type="button" class="pagination-button" data-page="${number}" aria-label="第 ${number} 頁" ${number === currentPage ? 'aria-current="page"' : ""}>${number}</button>`;
              }).join("")}
              <button type="button" class="pagination-button" data-page="${currentPage + 1}" ${currentPage === totalPages ? "disabled" : ""}>下一頁</button>
            </div>
          ` : ""}
        </nav>
      `;

      articleContent.innerHTML = `<div class="articles-grid">${articlesHtml}</div>${paginationHtml}`;

      articleContent.querySelectorAll("[data-page]").forEach((button) => {
        button.addEventListener("click", () => {
          renderArticles(Number(button.dataset.page));
          articleContent.focus({ preventScroll: true });
          const top = articleContent.getBoundingClientRect().top + window.scrollY - 90;
          window.scrollTo({ top, behavior: "instant" });
        });
      });
    };

    const renderSidebarTags = (tagCounts) => {
      if (!tagsFilterList) return;

      const sortedTags = Object.keys(tagCounts).sort((a, b) => {
        const diff = tagCounts[b] - tagCounts[a];
        return diff !== 0 ? diff : a.localeCompare(b, "zh-Hant");
      });

      const tagButton = (tag, label, count) => `
        <button type="button" class="tag-filter-btn" data-tag="${escapeHtml(tag)}" aria-pressed="false">
          <span class="tag-name">${escapeHtml(label)}</span>
          <span class="tag-count">${count}</span>
        </button>
      `;

      tagsFilterList.innerHTML =
        tagButton("ALL", "全部文章", allPosts.length) +
        sortedTags.map((tag) => tagButton(tag, tag, tagCounts[tag])).join("");

      tagsFilterList.querySelectorAll(".tag-filter-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          currentTag = btn.getAttribute("data-tag") || "ALL";
          updateURL();
          renderArticles();
          if (window.innerWidth <= 960) {
            const top = articleContent.getBoundingClientRect().top + window.scrollY - 90;
            window.scrollTo({ top, behavior: "smooth" });
          }
        });
      });
    };

    if (clearFilterBtn) clearFilterBtn.addEventListener("click", resetFilters);

    if (blogSearchInput) {
      blogSearchInput.addEventListener("input", (e) => {
        searchQuery = (e.target.value || "").trim();
        if (clearSearchBtn) clearSearchBtn.hidden = !searchQuery;
        renderArticles();
      });
    }

    if (clearSearchBtn) {
      clearSearchBtn.addEventListener("click", () => {
        if (blogSearchInput) {
          blogSearchInput.value = "";
          blogSearchInput.focus();
        }
        searchQuery = "";
        clearSearchBtn.hidden = true;
        renderArticles();
      });
    }

    const initArticles = (articles) => {
      allPosts = articles
        .map((item) => ({
          title: item.title,
          lead: item.lead,
          imageUrl: item.imageUrl,
          tags: item.tags || [],
          dateString: item.dateString || "",
          readTime: item.readTime || "約 5 分鐘閱讀",
          link: item.link,
          category: item.category || "",
        }))
        .sort((a, b) => b.dateString.localeCompare(a.dateString));

      // Without the catalog the server-rendered list stays; only filtering is lost.
      if (!allPosts.length) {
        if (tagsFilterList) {
          tagsFilterList.innerHTML =
            '<p class="widget-description">文章目錄沒有載入，暫時無法篩選。請重新整理頁面。</p>';
        }
        if (blogSearchInput) blogSearchInput.disabled = true;
        return;
      }

      const tagCounts = {};
      allPosts.forEach((post) => {
        post.tags.forEach((t) => {
          tagCounts[t] = (tagCounts[t] || 0) + 1;
        });
      });

      renderSidebarTags(tagCounts);
      renderArticles();
    };

    initArticles(window.__STATIC_ARTICLES__ || []);
  }

  const contactForm = document.getElementById("contact-form");
  if (contactForm) {
    const formStatus = document.getElementById("contact-form-status");
    const submitButton = contactForm.querySelector('button[type="submit"]');
    const showStatus = (state, message) => {
      if (!formStatus) return;
      formStatus.dataset.state = state;
      formStatus.textContent = message;
    };

    // The Worker at /api/contact emails the message through Resend.
    contactForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(contactForm));
      submitButton.disabled = true;
      contactForm.setAttribute("aria-busy", "true");
      showStatus("pending", "訊息傳送中…");
      try {
        const response = await fetch("/api/contact", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) {
          throw new Error(result.error || "目前無法送出訊息。");
        }
        contactForm.reset();
        showStatus("success", "已收到你的訊息，我會以電子郵件回覆。");
      } catch (error) {
        const reason =
          error instanceof TypeError ? "網路連線中斷，訊息尚未送出。" : error.message;
        showStatus("error", `${reason} 你也可以直接寄信到 rainbowh9490@gmail.com。`);
      } finally {
        submitButton.disabled = false;
        contactForm.removeAttribute("aria-busy");
      }
    });
  }
})();
=======
(() => {
  "use strict";

  const githubUser = "ian030590";

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

  // Storage can throw in private windows or with site data blocked.
  const readTheme = () => {
    try {
      return localStorage.getItem("theme");
    } catch (error) {
      return null;
    }
  };
  const saveTheme = (theme) => {
    try {
      localStorage.setItem("theme", theme);
    } catch (error) {
      // The toggle still works for this page view.
    }
  };

  const prefersDark = () =>
    Boolean(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);

  const getInitialTheme = () => {
    const savedTheme = readTheme();
    if (savedTheme === "dark" || savedTheme === "light") return savedTheme;
    return prefersDark() ? "dark" : "light";
  };

  const applyTheme = (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
    const label = theme === "dark" ? "切換至淺色模式" : "切換至深色模式";
    document.querySelectorAll(".theme-toggle").forEach((btn) => {
      const darkIcon = btn.querySelector(".icon-dark");
      const lightIcon = btn.querySelector(".icon-light");
      if (darkIcon && lightIcon) {
        darkIcon.style.display = theme === "dark" ? "none" : "inline-block";
        lightIcon.style.display = theme === "dark" ? "inline-block" : "none";
      }
      btn.setAttribute("aria-label", label);
      btn.setAttribute("title", label);
    });
  };

  applyTheme(getInitialTheme());

  document.querySelectorAll(".theme-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const currentTheme =
        document.documentElement.getAttribute("data-theme") || getInitialTheme();
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      saveTheme(nextTheme);
      applyTheme(nextTheme);
    });
  });

  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!readTheme()) applyTheme(e.matches ? "dark" : "light");
    });
  }

  document.querySelectorAll("[data-year]").forEach((node) => {
    node.textContent = new Date().getFullYear();
  });

  const menu = document.querySelector(".menu-button");
  const mobilePanel = document.querySelector(".mobile-panel");
  if (menu && mobilePanel) {
    const setMenu = (open) => {
      mobilePanel.classList.toggle("open", open);
      menu.classList.toggle("is-open", open);
      menu.setAttribute("aria-expanded", String(open));
      menu.setAttribute("aria-label", open ? "關閉選單" : "開啟選單");
    };
    menu.addEventListener("click", () => {
      setMenu(!mobilePanel.classList.contains("open"));
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && mobilePanel.classList.contains("open")) {
        setMenu(false);
        menu.focus();
      }
    });
  }

  const projectsGrid = document.getElementById("projects-grid");
  if (projectsGrid) {
    const projectsStatus = document.getElementById("projects-status");
    const snapshot = window.GITHUB_PROJECTS || { repositories: [] };
    const excludedRepos = [githubUser.toLowerCase(), "myportfolio"];

    const renderProjects = (repositories) => {
      if (!Array.isArray(repositories)) throw new Error("Invalid project list");
      const targetList = repositories.filter(
        (repo) =>
          !excludedRepos.includes(repo.name.toLowerCase()) && !repo.fork && !repo.private,
      );

      if (!targetList.length) {
        projectsGrid.innerHTML = '<p class="empty-state">尚無公開開源專案。</p>';
        return;
      }

      projectsGrid.innerHTML = targetList
        .map((repo) => {
          const topics = Array.isArray(repo.topics) ? repo.topics : [];
          const labels = [repo.archived ? "已封存" : null, repo.language, ...topics]
            .filter(Boolean)
            .slice(0, 4);
          // GitHub renders a 1200×630 preview per repository, or the uploaded social preview.
          const previewUrl = `https://opengraph.githubassets.com/1/${githubUser}/${repo.name}`;
          const updatedDate = new Date(repo.updated_at).toLocaleDateString("zh-TW", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          });
          const stars =
            repo.stargazers_count > 0
              ? `<span class="project-stars" title="${repo.stargazers_count} 個 GitHub 星號">
                  <span class="material-symbols-outlined" aria-hidden="true">star</span>
                  ${repo.stargazers_count}
                </span>`
              : "";

          return `
            <article class="project-card">
              <a class="card-link" href="${escapeHtml(repo.html_url)}" target="_blank" rel="noopener">
                <div class="project-visual">
                  <img
                    src="${escapeHtml(previewUrl)}"
                    alt=""
                    loading="lazy"
                    onerror="this.remove();"
                  />
                </div>
                <div class="project-content">
                  <div class="tags">${labels.map((label) => `<span class="tag">${escapeHtml(label)}</span>`).join("")}</div>
                  <h2>${escapeHtml(repo.name)}</h2>
                  ${repo.description ? `<p>${escapeHtml(repo.description)}</p>` : ""}
                  <div class="project-footer">
                    <span class="project-updated">更新於 ${escapeHtml(updatedDate)}</span>
                    <span class="project-footer-right">
                      ${stars}
                      <span class="text-link">在 GitHub 查看</span>
                    </span>
                  </div>
                </div>
              </a>
            </article>
          `;
        })
        .join("");
    };

    if (snapshot.repositories.length) {
      renderProjects(snapshot.repositories);
      if (projectsStatus) {
        projectsStatus.textContent = `目前顯示 ${snapshot.synced_at} 整理的公開專案，正在取得最新清單。`;
      }
    }

    fetch(
      `https://api.github.com/users/${githubUser}/repos?type=owner&sort=updated&direction=desc&per_page=100`,
    )
      .then((response) => {
        if (!response.ok) throw new Error("GitHub API request failed");
        return response.json();
      })
      .then((repositories) => {
        renderProjects(repositories);
        if (projectsStatus) projectsStatus.textContent = "已同步 GitHub 最新公開專案；已封存作品以標籤註明。";
      })
      .catch(() => {
        if (snapshot.repositories.length) {
          if (projectsStatus) projectsStatus.textContent = `目前顯示 ${snapshot.synced_at} 整理的公開專案；最新動態請見各專案的 GitHub 頁面。`;
          return;
        }
        if (projectsStatus) projectsStatus.textContent = "專案清單暫時無法更新。";
        projectsGrid.innerHTML = `
          <div class="empty-state">
            <p>GitHub 暫時沒有回應，請<a href="https://github.com/${githubUser}?tab=repositories" target="_blank" rel="noopener noreferrer">前往 GitHub 查看公開專案</a>。</p>
          </div>
        `;
      });
  }

  const articleContent = document.getElementById("article-content");
  const tagsFilterList = document.getElementById("tags-filter-list");
  const filterStatusBar = document.getElementById("filter-status-bar");
  const activeFilterName = document.getElementById("active-filter-name");
  const activeFilterCount = document.getElementById("active-filter-count");
  const clearFilterBtn = document.getElementById("clear-filter-btn");
  const blogSearchInput = document.getElementById("blog-search");
  const clearSearchBtn = document.getElementById("clear-search-btn");

  if (articleContent) {
    const articlesPerPage = 15;
    let allPosts = [];
    let currentTag = new URLSearchParams(window.location.search).get("tag") || "ALL";
    let searchQuery = "";

    const updateURL = () => {
      const url = new URL(window.location.href);
      if (currentTag && currentTag !== "ALL") {
        url.searchParams.set("tag", currentTag);
      } else {
        url.searchParams.delete("tag");
      }
      window.history.replaceState({}, "", url.toString());
    };

    const resetFilters = () => {
      currentTag = "ALL";
      searchQuery = "";
      if (blogSearchInput) blogSearchInput.value = "";
      if (clearSearchBtn) clearSearchBtn.hidden = true;
      updateURL();
      renderArticles();
    };

    const describeFilter = () => {
      if (currentTag !== "ALL" && searchQuery) return `標籤「${currentTag}」與關鍵字「${searchQuery}」`;
      if (currentTag !== "ALL") return `標籤「${currentTag}」`;
      return `關鍵字「${searchQuery}」`;
    };

    const renderArticles = (page = 1) => {
      const q = searchQuery.toLowerCase();
      const filtered = allPosts.filter((post) => {
        if (currentTag !== "ALL" && !post.tags.includes(currentTag)) return false;
        if (!q) return true;
        return (
          post.title.toLowerCase().includes(q) ||
          post.lead.toLowerCase().includes(q) ||
          post.tags.some((t) => t.toLowerCase().includes(q))
        );
      });

      const isFiltered = currentTag !== "ALL" || searchQuery.length > 0;
      if (filterStatusBar) {
        filterStatusBar.hidden = !isFiltered;
        if (isFiltered) {
          if (activeFilterName) activeFilterName.textContent = describeFilter();
          if (activeFilterCount) activeFilterCount.textContent = `(${filtered.length} 篇)`;
        }
      }

      if (tagsFilterList) {
        tagsFilterList.querySelectorAll(".tag-filter-btn").forEach((btn) => {
          const isActive = btn.getAttribute("data-tag") === currentTag;
          btn.classList.toggle("active", isActive);
          btn.setAttribute("aria-pressed", String(isActive));
        });
      }

      if (!filtered.length) {
        articleContent.innerHTML = `
          <div class="empty-state">
            <p>沒有符合${escapeHtml(describeFilter())}的文章。搜尋範圍是標題、摘要與標籤。</p>
            <button class="button-secondary reset-filter-btn" type="button">清除篩選條件</button>
          </div>
        `;
        articleContent.querySelector(".reset-filter-btn").addEventListener("click", resetFilters);
        return;
      }

      const showFeatured =
        currentTag === "ALL" && !searchQuery && page === 1 && filtered.length > 1;
      const totalPages = Math.max(1, Math.ceil(filtered.length / articlesPerPage));
      const currentPage = Math.max(1, Math.min(page, totalPages));
      const startIndex = (currentPage - 1) * articlesPerPage;
      const pagePosts = filtered.slice(startIndex, startIndex + articlesPerPage);

      const articlesHtml = pagePosts
        .map((post, index) => {
          const isFeatured = showFeatured && index === 0;
          const badge = isFeatured ? '<span class="featured-badge">最新專題</span>' : "";
          const tagsMarkup = post.tags
            .map((tag) => `<span class="card-tag-pill">${escapeHtml(tag)}</span>`)
            .join("");
          const imageMarkup = post.imageUrl
            ? `<div class="article-visual">
                <img src="${escapeHtml(post.imageUrl)}" alt="" loading="lazy" onerror="this.parentElement.classList.add('no-image'); this.remove();" />
                ${badge}
              </div>`
            : `<div class="article-visual no-image">${badge}</div>`;

          return `
            <article class="article-card ${isFeatured ? "article-card--featured" : ""}">
              <a class="card-link" href="${escapeHtml(post.link)}">
                ${imageMarkup}
                <div class="article-content">
                  <div class="card-tags-row">${tagsMarkup}</div>
                  <h2 class="article-title">${escapeHtml(post.title)}</h2>
                  <div class="article-meta">
                    <time datetime="${escapeHtml(post.dateString)}">${escapeHtml(post.dateString)}</time>
                    <span>${escapeHtml(post.readTime)}</span>
                  </div>
                  <p class="article-excerpt">${escapeHtml(post.lead)}</p>
                  <div class="article-footer">
                    <span class="source-kicker">${escapeHtml(post.category)}</span>
                    <span class="read-more-link">閱讀全文</span>
                  </div>
                </div>
              </a>
            </article>
          `;
        })
        .join("");

      const paginationHtml = `
        <nav class="article-pagination" aria-label="文章分頁">
          <p class="article-page-status" role="status">第 ${startIndex + 1} 至 ${startIndex + pagePosts.length} 篇，共 ${filtered.length} 篇</p>
          ${totalPages > 1 ? `
            <div class="pagination-controls">
              <button type="button" class="pagination-button" data-page="${currentPage - 1}" ${currentPage === 1 ? "disabled" : ""}>上一頁</button>
              ${Array.from({ length: totalPages }, (_, index) => {
                const number = index + 1;
                return `<button type="button" class="pagination-button" data-page="${number}" aria-label="第 ${number} 頁" ${number === currentPage ? 'aria-current="page"' : ""}>${number}</button>`;
              }).join("")}
              <button type="button" class="pagination-button" data-page="${currentPage + 1}" ${currentPage === totalPages ? "disabled" : ""}>下一頁</button>
            </div>
          ` : ""}
        </nav>
      `;

      articleContent.innerHTML = `<div class="articles-grid">${articlesHtml}</div>${paginationHtml}`;

      articleContent.querySelectorAll("[data-page]").forEach((button) => {
        button.addEventListener("click", () => {
          renderArticles(Number(button.dataset.page));
          articleContent.focus({ preventScroll: true });
          const top = articleContent.getBoundingClientRect().top + window.scrollY - 90;
          window.scrollTo({ top, behavior: "instant" });
        });
      });
    };

    const renderSidebarTags = (tagCounts) => {
      if (!tagsFilterList) return;

      const sortedTags = Object.keys(tagCounts).sort((a, b) => {
        const diff = tagCounts[b] - tagCounts[a];
        return diff !== 0 ? diff : a.localeCompare(b, "zh-Hant");
      });

      const tagButton = (tag, label, count) => `
        <button type="button" class="tag-filter-btn" data-tag="${escapeHtml(tag)}" aria-pressed="false">
          <span class="tag-name">${escapeHtml(label)}</span>
          <span class="tag-count">${count}</span>
        </button>
      `;

      tagsFilterList.innerHTML =
        tagButton("ALL", "全部文章", allPosts.length) +
        sortedTags.map((tag) => tagButton(tag, tag, tagCounts[tag])).join("");

      tagsFilterList.querySelectorAll(".tag-filter-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          currentTag = btn.getAttribute("data-tag") || "ALL";
          updateURL();
          renderArticles();
          if (window.innerWidth <= 960) {
            const top = articleContent.getBoundingClientRect().top + window.scrollY - 90;
            window.scrollTo({ top, behavior: "smooth" });
          }
        });
      });
    };

    if (clearFilterBtn) clearFilterBtn.addEventListener("click", resetFilters);

    if (blogSearchInput) {
      blogSearchInput.addEventListener("input", (e) => {
        searchQuery = (e.target.value || "").trim();
        if (clearSearchBtn) clearSearchBtn.hidden = !searchQuery;
        renderArticles();
      });
    }

    if (clearSearchBtn) {
      clearSearchBtn.addEventListener("click", () => {
        if (blogSearchInput) {
          blogSearchInput.value = "";
          blogSearchInput.focus();
        }
        searchQuery = "";
        clearSearchBtn.hidden = true;
        renderArticles();
      });
    }

    const initArticles = (articles) => {
      allPosts = articles
        .map((item) => ({
          title: item.title,
          lead: item.lead,
          imageUrl: item.imageUrl,
          tags: item.tags || [],
          dateString: item.dateString || "",
          readTime: item.readTime || "約 5 分鐘閱讀",
          link: item.link,
          category: item.category || "",
        }))
        .sort((a, b) => b.dateString.localeCompare(a.dateString));

      // Without the catalog the server-rendered list stays; only filtering is lost.
      if (!allPosts.length) {
        if (tagsFilterList) {
          tagsFilterList.innerHTML =
            '<p class="widget-description">文章目錄沒有載入，暫時無法篩選。請重新整理頁面。</p>';
        }
        if (blogSearchInput) blogSearchInput.disabled = true;
        return;
      }

      const tagCounts = {};
      allPosts.forEach((post) => {
        post.tags.forEach((t) => {
          tagCounts[t] = (tagCounts[t] || 0) + 1;
        });
      });

      renderSidebarTags(tagCounts);
      renderArticles();
    };

    initArticles(window.__STATIC_ARTICLES__ || []);
  }

  const contactForm = document.getElementById("contact-form");
  if (contactForm) {
    const formStatus = document.getElementById("contact-form-status");
    contactForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(contactForm);
      const subject = data.get("subject");
      const name = data.get("name");
      const role = data.get("role");
      const email = data.get("email");
      const body = data.get("body");
      window.location.href = `mailto:rainbowh9490@gmail.com?subject=${encodeURIComponent(`[Website Contact] ${subject} - ${name}`)}&body=${encodeURIComponent(`From: ${name}\nRole: ${role}\nEmail: ${email}\n\n${body}`)}`;
      if (formStatus) {
        formStatus.textContent =
          "已嘗試開啟郵件軟體。如果沒有出現新郵件，請直接寄信到 rainbowh9490@gmail.com。";
      }
    });
  }
})();
>>>>>>> 0fb27403d877d5709ef65c142ca63b6d1e56b269
