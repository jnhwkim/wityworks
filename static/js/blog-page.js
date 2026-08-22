(function () {
  var COOKIE_NAME = "theme";

  function readCookie(name) {
    var match = document.cookie.match(
      new RegExp("(?:^|; )" + name + "=([^;]*)"),
    );
    return match ? decodeURIComponent(match[1]) : null;
  }

  function writeCookie(name, value) {
    document.cookie =
      name +
      "=" +
      encodeURIComponent(value) +
      ";path=/;max-age=31536000;SameSite=Lax";
  }

  function applyTheme(mode) {
    if (mode === "light" || mode === "dark") {
      document.documentElement.setAttribute("data-theme", mode);
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
    var buttons = document.querySelectorAll(".theme-toggle button");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute(
        "aria-pressed",
        buttons[i].getAttribute("data-mode") === mode ? "true" : "false",
      );
    }
  }

  function setTheme(mode) {
    writeCookie(COOKIE_NAME, mode);
    applyTheme(mode);
  }

  var saved = readCookie(COOKIE_NAME) || "system";
  applyTheme(saved);

  var toggle = document.querySelector(".theme-toggle");
  toggle.addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-mode]");
    if (!btn) return;
    setTheme(btn.getAttribute("data-mode"));
  });
})();

(function () {
  // Kept in sync with the same nav-row-divider logic in the root
  // index.html — see the comments there for why each piece exists.
  // Blog's nav has no in-page hash links, so scroll-spy is omitted.
  var nav = document.querySelector("nav.primary");
  if (!nav) return;
  var navLinks = Array.prototype.slice.call(nav.querySelectorAll("a"));
  if (!navLinks.length) return;

  function setNavHeightVar() {
    document.documentElement.style.setProperty(
      "--nav-height",
      nav.getBoundingClientRect().height + "px",
    );
  }

  var ROW_MARGIN_TOP = "-1px";
  var DIVIDER_OFFSET = -1;
  var LAST_ROW_MARGIN_BOTTOM = "-0.5px";

  function updateNavRowDividers() {
    var oldDividers = nav.querySelectorAll(".nav-row-divider");
    for (var i = 0; i < oldDividers.length; i++) oldDividers[i].remove();
    navLinks.forEach(function (link) {
      link.style.marginTop = "";
      link.style.marginBottom = "";
      link.style.borderBottomColor = "";
    });

    var navTop = nav.getBoundingClientRect().top;
    var rows = [];
    navLinks.forEach(function (link) {
      var top = Math.round(link.getBoundingClientRect().top - navTop);
      var row = null;
      for (var j = 0; j < rows.length; j++) {
        if (Math.abs(rows[j].top - top) < 3) {
          row = rows[j];
          break;
        }
      }
      if (!row) {
        row = { top: top, links: [] };
        rows.push(row);
      }
      row.links.push(link);
    });
    rows.sort(function (a, b) {
      return a.top - b.top;
    });

    if (rows.length >= 2) {
      for (var r = 1; r < rows.length; r++) {
        var divider = document.createElement("div");
        divider.className = "nav-row-divider";
        divider.style.top = rows[r].top + DIVIDER_OFFSET + "px";
        nav.appendChild(divider);
      }

      for (var r2 = 1; r2 < rows.length; r2++) {
        rows[r2].links.forEach(function (link) {
          link.style.marginTop = ROW_MARGIN_TOP;
        });
      }
    }

    rows[rows.length - 1].links.forEach(function (link) {
      link.style.borderBottomColor = "transparent";
      link.style.marginBottom = LAST_ROW_MARGIN_BOTTOM;
    });
  }

  setNavHeightVar();
  updateNavRowDividers();
  window.addEventListener("resize", function () {
    setNavHeightVar();
    updateNavRowDividers();
  });
})();

(function () {
  var content = document.getElementById("blog-content");
  var heading = document.getElementById("blog-heading");
  var eyebrow = document.getElementById("blog-eyebrow");
  var note = document.getElementById("blog-note");
  var catContainer = document.getElementById("blog-cat-container");
  var blogCols = document.getElementById("blog-cols");
  var expandWrapper = document.getElementById("cat-expand-wrapper");
  var minBtn = document.getElementById("cat-minimize-btn");
  var expBtn = document.getElementById("cat-expand-btn");
  var params = new URLSearchParams(location.search);

  var SIDEBAR_COOKIE = "blog_sidebar";

  function readCookie(name) {
    var match = document.cookie.match(
      new RegExp("(?:^|; )" + name + "=([^;]*)"),
    );
    return match ? decodeURIComponent(match[1]) : null;
  }

  function writeCookie(name, value) {
    document.cookie =
      name +
      "=" +
      encodeURIComponent(value) +
      ";path=/;max-age=31536000;SameSite=Lax";
  }

  function applySidebarState(state) {
    if (!blogCols) return;
    if (state === "collapsed") {
      blogCols.classList.add("sidebar-collapsed");
      if (expandWrapper) expandWrapper.removeAttribute("hidden");
      if (minBtn) minBtn.setAttribute("aria-expanded", "false");
    } else {
      blogCols.classList.remove("sidebar-collapsed");
      if (expandWrapper) expandWrapper.setAttribute("hidden", "");
      if (minBtn) minBtn.setAttribute("aria-expanded", "true");
    }
  }

  function setSidebarState(state) {
    writeCookie(SIDEBAR_COOKIE, state);
    applySidebarState(state);
  }

  var savedSidebar = readCookie(SIDEBAR_COOKIE) || "expanded";
  applySidebarState(savedSidebar);

  if (minBtn) {
    minBtn.addEventListener("click", function () {
      setSidebarState("collapsed");
    });
  }

  if (expBtn) {
    expBtn.addEventListener("click", function () {
      setSidebarState("expanded");
    });
  }

  function formatDate(iso) {
    var d = new Date(iso + "T00:00:00");
    if (isNaN(d)) return iso;
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[c];
    });
  }

  function renderMath(root) {
    if (window.renderMathInElement) {
      renderMathInElement(root, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false },
        ],
      });
    }
  }

  function categoryList(activeSlug) {
    var ul = document.createElement("ul");
    ul.className = "cat-list";
    var all = document.createElement("li");
    var allLink = document.createElement("a");
    allLink.href = "/blog/";
    allLink.textContent = "All";
    if (!activeSlug) allLink.className = "active";
    var allCount = BLOG_POSTS.filter(function (p) {
      return p.visibility === "public";
    }).length;
    var allCountSpan = document.createElement("span");
    allCountSpan.className = "count";
    allCountSpan.textContent = allCount;
    allLink.appendChild(allCountSpan);
    all.appendChild(allLink);
    ul.appendChild(all);
    BLOG_CATEGORIES.forEach(function (cat) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "/blog/?category=" + encodeURIComponent(cat.slug);
      a.innerHTML = cat.label;
      if (cat.slug === activeSlug) a.className += " active";
      var count = BLOG_POSTS.filter(function (p) {
        return p.category === cat.slug && p.visibility === "public";
      }).length;
      var countSpan = document.createElement("span");
      countSpan.className = "count";
      countSpan.textContent = count;
      a.appendChild(countSpan);
      li.appendChild(a);
      ul.appendChild(li);
    });
    return ul;
  }

  function renderCategories(activeSlug) {
    if (!catContainer) return;
    catContainer.innerHTML = "";
    catContainer.appendChild(categoryList(activeSlug));
  }

  function postCard(post) {
    var article = document.createElement("article");
    article.className = "post-card";
    var cardContent = document.createElement("div");
    cardContent.className = "post-card-content";
    var cardEyebrow = document.createElement("span");
    cardEyebrow.className = "label eyebrow";
    cardEyebrow.innerHTML = post.categoryLabel;
    var h3 = document.createElement("h3");
    var a = document.createElement("a");
    a.href = "/blog/" + encodeURIComponent(post.category) + "/" + encodeURIComponent(post.slug) + "/";
    a.textContent = post.title;
    h3.appendChild(a);
    var p = document.createElement("p");
    p.innerHTML = post.summary;
    var meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = formatDate(post.date) + " · " + post.readTime;
    cardContent.appendChild(cardEyebrow);
    cardContent.appendChild(h3);
    cardContent.appendChild(p);
    cardContent.appendChild(meta);
    if (post.cover) {
      article.classList.add("has-cover");
      var coverLink = document.createElement("a");
      coverLink.className = "post-card-cover";
      coverLink.href = a.href;
      var cover = document.createElement("img");
      cover.src = post.cover;
      cover.alt = "";
      cover.loading = "lazy";
      coverLink.appendChild(cover);
      article.appendChild(coverLink);
    }
    article.appendChild(cardContent);
    return article;
  }

  function renderListing(activeSlug) {
    if (eyebrow) eyebrow.textContent = "Writing";
    heading.textContent = "Blog";
    note.innerHTML =
      'Research notes, paper reviews, and essays on AI, math, and life.<a class="rss-link blog-rss-link" href="/blog/rss.xml" type="application/rss+xml" title="Subscribe to the Blog RSS Feed"><svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><circle cx="3.1" cy="12.9" r="1.35" fill="currentColor"/><path d="M2 7.1a6.9 6.9 0 0 1 6.9 6.9M2 2a12 12 0 0 1 12 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg><span>RSS</span></a>';
    content.innerHTML = "";

    renderCategories(activeSlug);

    var posts = BLOG_POSTS.filter(function (p) {
      return (
        p.visibility === "public" && (!activeSlug || p.category === activeSlug)
      );
    });

    if (!posts.length) {
      var empty = document.createElement("p");
      empty.className = "post-empty";
      empty.textContent = "No public posts here yet — check back soon.";
      content.appendChild(empty);
    } else {
      posts.forEach(function (p) {
        content.appendChild(postCard(p));
      });
    }
  }

  function renderPrivateNotice(label) {
    content.innerHTML = "";
    var div = document.createElement("div");
    div.className = "post-empty";
    div.textContent = label || "This post hasn't been published yet.";
    content.appendChild(div);
    var back = document.createElement("p");
    var a = document.createElement("a");
    a.href = "./";
    a.textContent = "← Back to Blog";
    back.appendChild(a);
    content.appendChild(back);
  }

  function parseFrontmatter(text) {
    var m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
    if (!m) return { data: {}, body: text };
    var data = {};
    m[1].split(/\r?\n/).forEach(function (line) {
      var idx = line.indexOf(":");
      if (idx === -1) return;
      data[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    });
    return { data: data, body: m[2] };
  }

  function slugify(text) {
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .replace(/[\s_]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function getXPostId(url) {
    try {
      var parsed = new URL(url);
      var host = parsed.hostname.toLowerCase().replace(/^www\./, "");
      if (host !== "x.com" && host !== "twitter.com") return null;
      var match = parsed.pathname.match(/\/status\/(\d+)/);
      return match ? match[1] : null;
    } catch (e) {
      return null;
    }
  }

  function xConversation(postUrl) {
    var postId = getXPostId(postUrl);
    if (!postId) return null;

    var reply = document.createElement("a");
    reply.className = "show-all-btn show-all-btn--sm x-conversation-reply";
    reply.href = "https://x.com/intent/tweet?in_reply_to=" + postId;
    reply.target = "_blank";
    reply.rel = "noopener noreferrer";
    reply.textContent = "𝕏 Join the conversation";
    return reply;
  }

  function renderPost(pathParam) {
    var parts = pathParam.split("/");
    var category = parts[0];
    var slug = parts.slice(1).join("/");
    var entry = BLOG_POSTS.filter(function (p) {
      return p.category === category && p.slug === slug;
    })[0];

    if (!entry) {
      renderCategories(null);
      renderPrivateNotice("Post not found.");
      return;
    }
    if (entry.visibility !== "public") {
      renderCategories(entry.category);
      renderPrivateNotice("This post isn't published yet.");
      return;
    }

    renderCategories(entry.category);

    fetch("/blog/" + category + "/" + slug + ".md")
      .then(function (res) {
        if (!res.ok) throw new Error("fetch failed");
        return res.text();
      })
      .then(function (text) {
        var parsed = parseFrontmatter(text);
        if ((parsed.data.visibility || "").trim() !== "public") {
          renderPrivateNotice("This post isn't published yet.");
          return;
        }
        if (eyebrow) {
          var categoryLink = document.createElement("a");
          categoryLink.href =
            "/blog/?category=" + encodeURIComponent(entry.category);
          categoryLink.textContent =
            parsed.data.categoryLabel || entry.categoryLabel;
          eyebrow.innerHTML = "";
          eyebrow.appendChild(categoryLink);
        }
        heading.textContent = parsed.data.title || entry.title;
        note.innerHTML = "";
        content.innerHTML = "";

        var article = document.createElement("article");
        article.className = "post-body";

        var meta = document.createElement("p");
        meta.className = "meta";
        var metaDetails = document.createElement("span");
        metaDetails.className = "post-meta-details";
        metaDetails.textContent =
          formatDate(parsed.data.date || entry.date) +
          " · " +
          (parsed.data.readTime || entry.readTime);
        var rssLink = document.createElement("a");
        rssLink.className = "rss-link post-rss-link";
        rssLink.href = "rss.xml";
        rssLink.type = "application/rss+xml";
        rssLink.title = "Subscribe to the Blog RSS Feed";
        rssLink.innerHTML =
          '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><circle cx="3.1" cy="12.9" r="1.35" fill="currentColor"/><path d="M2 7.1a6.9 6.9 0 0 1 6.9 6.9M2 2a12 12 0 0 1 12 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg><span>RSS</span>';
        meta.appendChild(metaDetails);
        meta.appendChild(rssLink);
        var body = document.createElement("div");

        if (window.marked) {
          var isAfterHr = false;

          marked.use({
            renderer: {
              heading(text, level) {
                isAfterHr = false;
                var plainText = text.replace(/<[^>]*>/g, "");
                var id = slugify(plainText);
                return (
                  "<h" +
                  level +
                  ' id="' +
                  id +
                  '">' +
                  text +
                  "</h" +
                  level +
                  ">"
                );
              },
              hr() {
                isAfterHr = true;
                return "<hr>\n";
              },
              paragraph(text) {
                if (isAfterHr) {
                  isAfterHr = false;
                  return '<p><em class="footnote">' + text + "</em></p>\n";
                }
                return "<p>" + text + "</p>\n";
              },
            },
          });
        }

        body.innerHTML = window.marked
          ? marked.parse(parsed.body)
          : escapeHtml(parsed.body);

        var coverSource = parsed.data.cover || entry.cover;
        if (coverSource) {
          var coverFigure = document.createElement("figure");
          coverFigure.className = "post-cover";
          var coverImage = document.createElement("img");
          coverImage.src = coverSource;
          coverImage.alt = parsed.data.title || entry.title;
          coverFigure.appendChild(coverImage);
          body.insertBefore(coverFigure, body.firstChild);
        }

        var tocHeading = body.querySelector("h2");
        if (
          tocHeading &&
          tocHeading.textContent.trim().toLowerCase() === "table of contents"
        ) {
          var tocList = tocHeading.nextElementSibling;
          if (tocList && /^(UL|OL)$/.test(tocList.tagName)) {
            var tocCard = document.createElement("section");
            tocCard.className = "toc-card";
            tocCard.setAttribute("aria-label", "Table of contents");
            tocHeading.parentNode.insertBefore(tocCard, tocHeading);
            tocCard.appendChild(tocHeading);
            tocCard.appendChild(tocList);
            tocCard.querySelectorAll("a").forEach(function (link) {
              var match = link.textContent.match(/^(\d+(?:\.\d+)*\.?)\s+(.+)$/);
              if (!match) {
                link.classList.add("toc-link--unnumbered");
                return;
              }
              var number = document.createElement("span");
              number.className = "toc-number";
              number.textContent = match[1];
              link.textContent = "";
              link.appendChild(number);
              link.appendChild(document.createTextNode(match[2]));
            });
          }
        }

        article.appendChild(meta);
        article.appendChild(body);
        content.appendChild(article);

        var endMark = document.createElement("div");
        endMark.className = "post-end-mark";
        endMark.setAttribute("aria-hidden", "true");
        endMark.innerHTML =
          '<svg viewBox="0 0 12 16" width="11" height="15">' +
          '<rect x="5.2" y="1" width="1.6" height="14" fill="var(--gold)"/>' +
          '<rect x="1" y="4.4" width="10" height="1.6" fill="var(--gold)"/>' +
          "</svg>";
        content.appendChild(endMark);

        var actions = document.createElement("div");
        actions.className = "post-actions";
        var a = document.createElement("a");
        a.className = "show-all-btn show-all-btn--sm post-back-btn";
        a.href = "/blog/?category=" + encodeURIComponent(category);
        a.textContent =
          "← Back to " +
          (parsed.data.categoryLabel || entry.categoryLabel).replace(
            /&amp;/g,
            "&",
          );
        actions.appendChild(a);

        var conversation = xConversation(parsed.data.xPostUrl || "");
        if (conversation) actions.appendChild(conversation);
        content.appendChild(actions);

        renderMath(body);
      })
      .catch(function () {
        renderPrivateNotice("This post couldn't be loaded.");
      });
  }

  var postParam = document.body.getAttribute("data-blog-post") || params.get("post");
  var categoryParam = params.get("category");

  if (postParam) {
    renderPost(postParam);
  } else {
    renderListing(categoryParam);
  }
})();
