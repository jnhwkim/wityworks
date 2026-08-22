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
  var catList = document.getElementById("home-blog-cats");
  var postList = document.getElementById("home-blog-posts");
  var homeCols = document.getElementById("home-blog-cols");
  var expandWrapper = document.getElementById("home-cat-expand-wrapper");
  var minBtn = document.getElementById("home-cat-minimize-btn");
  var expBtn = document.getElementById("home-cat-expand-btn");
  if (!catList || !postList || typeof BLOG_POSTS === "undefined") return;

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
    if (!homeCols) return;
    if (state === "collapsed") {
      homeCols.classList.add("sidebar-collapsed");
      if (expandWrapper) expandWrapper.removeAttribute("hidden");
      if (minBtn) minBtn.setAttribute("aria-expanded", "false");
    } else {
      homeCols.classList.remove("sidebar-collapsed");
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

  var publicPosts = BLOG_POSTS.filter(function (p) {
    return p.visibility === "public";
  });

  var allLi = document.createElement("li");
  var allA = document.createElement("a");
  allA.href = "/blog/";
  allA.className = "active";
  allA.innerHTML = 'All <span class="count">' + publicPosts.length + "</span>";
  allLi.appendChild(allA);
  catList.appendChild(allLi);

  BLOG_CATEGORIES.forEach(function (cat) {
    var count = publicPosts.filter(function (p) {
      return p.category === cat.slug;
    }).length;
    var li = document.createElement("li");
    var a = document.createElement("a");
    a.href = "/blog/?category=" + encodeURIComponent(cat.slug);
    a.innerHTML = cat.label + ' <span class="count">' + count + "</span>";
    li.appendChild(a);
    catList.appendChild(li);
  });

  function formatDate(iso) {
    var d = new Date(iso + "T00:00:00");
    if (isNaN(d)) return iso;
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  publicPosts.forEach(function (post) {
    var article = document.createElement("article");
    article.className = "post-card";
    var cardContent = document.createElement("div");
    cardContent.className = "post-card-content";
    var eyebrow = document.createElement("span");
    eyebrow.className = "label eyebrow";
    eyebrow.innerHTML = post.categoryLabel;
    var h3 = document.createElement("h3");
    var a = document.createElement("a");
    a.href =
      "/blog/" +
      encodeURIComponent(post.category) +
      "/" +
      encodeURIComponent(post.slug) +
      "/";
    a.textContent = post.title;
    h3.appendChild(a);
    var p = document.createElement("p");
    p.innerHTML = post.summary;
    var meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = formatDate(post.date) + " · " + post.readTime;
    cardContent.appendChild(eyebrow);
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
    postList.appendChild(article);
  });
})();

(function () {
  var courses = document.getElementById("teaching-courses");
  var showAllBtn = document.getElementById("teaching-show-all");
  var showLessBtn = document.getElementById("teaching-show-less");
  if (!courses || !showAllBtn || !showLessBtn) return;
  if (courses.querySelectorAll(".course-card").length <= 2) {
    showAllBtn.hidden = true;
    return;
  }

  courses.classList.add("collapsed");

  showAllBtn.addEventListener("click", function () {
    courses.classList.remove("collapsed");
    showAllBtn.hidden = true;
    showLessBtn.hidden = false;
  });
  showLessBtn.addEventListener("click", function () {
    courses.classList.add("collapsed");
    showAllBtn.hidden = false;
    showLessBtn.hidden = true;
  });
})();

(function () {
  var nav = document.querySelector("nav.primary");
  if (!nav) return;
  var navLinks = Array.prototype.slice.call(
    nav.querySelectorAll('a[href^="#"]'),
  );
  var sections = navLinks
    .map(function (link) {
      return document.querySelector(link.getAttribute("href"));
    })
    .filter(Boolean);
  if (!sections.length) return;

  function setNavHeightVar() {
    document.documentElement.style.setProperty(
      "--nav-height",
      nav.getBoundingClientRect().height + "px",
    );
  }

  // When the nav wraps to 2+ rows (a narrow viewport, or simply more menu
  // items than fit on one line), draw a full-width divider — edge-to-edge
  // like the nav's own border-top/border-bottom — at each row boundary.
  // Group links by their rendered top (rounded, to absorb sub-pixel
  // rounding differences between items), one divider per gap between
  // consecutive rows. Works for any number of rows, not just 2.
  // Row 2+ links get an explicit marginTop (the CSS default is -1px),
  // and the row divider gets its own pixel offset from the *pre-shift*
  // row position — the two are independently tunable, not tied to each
  // other, since they don't necessarily need to move by the same amount.
  var ROW_MARGIN_TOP = "-1px";
  var DIVIDER_OFFSET = -1;
  var LAST_ROW_MARGIN_BOTTOM = "-0.5px";

  function updateNavRowDividers() {
    var oldDividers = nav.querySelectorAll(".nav-row-divider");
    for (var i = 0; i < oldDividers.length; i++) oldDividers[i].remove();
    // Undo any row-shift from a previous call before re-measuring — which
    // links fall in row 2+ can change between calls (resize, item count).
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
      // Place dividers using each row's *pre-shift* top (captured above,
      // at the CSS-default -1px margin) plus DIVIDER_OFFSET — independent
      // of whatever ROW_MARGIN_TOP does to the links themselves.
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

    // The bottom-most row's own border-bottom (light var(--line-soft), same
    // as every other per-link grid border) sits directly above nav's own
    // outer border-bottom (thick, var(--ink)) and paints on top of it (child
    // borders paint after the parent's), so it visually pokes out as a
    // lighter sliver instead of blending into the thick line. Applies
    // whether the nav is a single row (desktop) or wraps (mobile) — it's
    // always the last row that touches nav's outer border-bottom. Hide that
    // border and pull the row up LAST_ROW_MARGIN_BOTTOM so only nav's own
    // thick border-bottom shows, nudged up half a pixel to line up cleanly.
    rows[rows.length - 1].links.forEach(function (link) {
      link.style.borderBottomColor = "transparent";
      link.style.marginBottom = LAST_ROW_MARGIN_BOTTOM;
    });
  }

  function updateScrollSpy() {
    var navHeight = nav.getBoundingClientRect().height;
    var current = sections[0];
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].getBoundingClientRect().top <= navHeight + 4) {
        current = sections[i];
      } else {
        break;
      }
    }
    navLinks.forEach(function (link) {
      var isCurrent = link.getAttribute("href") === "#" + current.id;
      link.setAttribute("aria-current", isCurrent ? "page" : "false");
    });
  }

  // Shared with the on-load hash-scroll correction below, so both paths
  // (clicking a nav link, and loading/refreshing a URL that already has a
  // matching #hash) land on the exact same pixel.
  function computeTargetTop(target) {
    var navHeight = nav.getBoundingClientRect().height;
    // Land the section's own top border on the exact same pixel row as
    // nav's border-bottom (rather than just underneath it), so the two
    // 2px borders coincide into one line instead of stacking into a
    // visually doubled-thickness band.
    var navBorderWidth =
      parseFloat(getComputedStyle(nav).borderBottomWidth) || 0;
    var safetyMargin = 1;
    return Math.max(
      Math.round(
        target.getBoundingClientRect().top +
          window.scrollY -
          navHeight +
          navBorderWidth +
          safetyMargin,
      ),
      0,
    );
  }

  // Incremented on every scrollToTarget() call so a stale poll loop from an
  // earlier click (still in-flight when a new nav click interrupts it) can
  // detect it's been superseded and bail out instead of firing its
  // corrective scrollBy against a target the user already scrolled away from.
  var scrollGeneration = 0;

  function scrollToTarget(target, smooth) {
    var myGeneration = ++scrollGeneration;
    window.scrollTo({
      top: computeTargetTop(target),
      behavior: smooth ? "smooth" : "auto",
    });
    // Smooth-scroll animations settle a pixel or two off the requested
    // target (browser-dependent rounding); correct once things have
    // settled so every section lines up identically. The correction is
    // measurement-based (actual on-screen gap between nav's bottom and
    // the target's top) rather than re-deriving computeTargetTop's
    // formula again, since that formula assumes nav is fully *stuck* —
    // only reliably true well after scrolling has fully settled.
    //
    // On mobile Safari specifically, navigating "up" toward the top of
    // the page (e.g. Blog → Teaching → Publications) tends to bring the
    // address bar back, which resizes the visual viewport *after* the
    // scroll/scrollend has already fired. Rather than repeatedly jump-
    // correcting (which looked like an overshoot-then-snap-back), this
    // only *measures* every 120ms until the gap itself stops changing
    // between checks (i.e. the address bar has actually finished
    // resizing) — then applies at most one smooth correction, so there's
    // a single continuous easing motion instead of a jarring re-jump.
    var navBorderWidth =
      parseFloat(getComputedStyle(nav).borderBottomWidth) || 0;
    var desiredGap = -(navBorderWidth + 1);
    var lastGap = null;
    var stableCount = 0;
    var attempts = 0;
    var maxAttempts = 20; // ~2.4s ceiling so a pathological case can't loop forever

    function poll() {
      if (myGeneration !== scrollGeneration) return; // superseded by a newer nav click
      attempts++;
      var actualGap =
        target.getBoundingClientRect().top - nav.getBoundingClientRect().bottom;
      if (lastGap !== null && Math.abs(actualGap - lastGap) < 0.5) {
        stableCount++;
      } else {
        stableCount = 0;
      }
      lastGap = actualGap;
      if (stableCount < 2 && attempts < maxAttempts) {
        setTimeout(poll, 120);
        return;
      }
      if (Math.abs(actualGap - desiredGap) > 0.5) {
        window.scrollBy({ top: actualGap - desiredGap, behavior: "smooth" });
      }
    }
    setTimeout(poll, 400);
  }

  nav.addEventListener("click", function (e) {
    var link = e.target.closest('a[href^="#"]');
    if (!link) return;
    var target = document.querySelector(link.getAttribute("href"));
    if (!target) return;
    e.preventDefault();
    scrollToTarget(target, true);
    if (history.pushState)
      history.pushState(null, "", link.getAttribute("href"));
  });

  setNavHeightVar();
  updateNavRowDividers();
  updateScrollSpy();

  // The browser's own native hash-scroll (on initial load, or a refresh of
  // a URL that already carries a #hash from a previous nav click) only
  // knows about CSS scroll-margin-top, not this exact-pixel-overlap
  // correction — redo it ourselves once layout has settled.
  if (location.hash) {
    var initialTarget = document.querySelector(location.hash);
    if (initialTarget) {
      setTimeout(function () {
        scrollToTarget(initialTarget, false);
      }, 0);
    }
  }

  window.addEventListener("scroll", updateScrollSpy, { passive: true });
  window.addEventListener("resize", function () {
    setNavHeightVar();
    updateNavRowDividers();
    updateScrollSpy();
  });
})();

(function () {
  var COLLAPSE_LIMIT = 7;
  var topicFilter = document.querySelector(".pub-filters");
  var pubList = document.getElementById("pub-list");
  var pubItems = Array.prototype.slice.call(
    document.querySelectorAll("#pub-list .pub-item"),
  );
  var showAllBtn = document.getElementById("pub-show-all");
  var showLessBtn = document.getElementById("pub-show-less");
  if (
    !topicFilter ||
    !pubList ||
    !pubItems.length ||
    !showAllBtn ||
    !showLessBtn
  )
    return;

  var filterLinks = Array.prototype.slice.call(
    topicFilter.querySelectorAll("a[data-topic]"),
  );
  var currentTopic = "featured";
  var expanded = false;

  function matchesTopic(item, topic) {
    if (topic === "all") return true;
    if (topic === "featured")
      return item.getAttribute("data-featured") === "true";
    if (topic.indexOf("year:") === 0)
      return item.getAttribute("data-year") === topic.slice(5);
    if (topic.indexOf("venue:") === 0)
      return item.getAttribute("data-venue") === topic.slice(6);
    var topics = (item.getAttribute("data-topics") || "").split(" ");
    return topics.indexOf(topic) !== -1;
  }

  function updateBadges() {
    filterLinks.forEach(function (link) {
      var topic = link.getAttribute("data-topic");
      var badge = link.querySelector(".filter-count");
      if (!badge) return;
      var count = pubItems.filter(function (item) {
        return matchesTopic(item, topic);
      }).length;
      badge.textContent = count;
    });
  }

  function render() {
    var visibleCount = 0;
    var totalMatching = 0;
    var firstVisibleItem = null;
    pubItems.forEach(function (item) {
      var matches = matchesTopic(item, currentTopic);
      item.classList.remove("pub-item--first-visible");
      if (!matches) {
        item.style.display = "none";
        return;
      }
      totalMatching++;
      if (
        currentTopic === "all" &&
        !expanded &&
        visibleCount >= COLLAPSE_LIMIT
      ) {
        item.style.display = "none";
      } else {
        item.style.display = "";
        visibleCount++;
        if (!firstVisibleItem) firstVisibleItem = item;
      }
    });
    if (firstVisibleItem)
      firstVisibleItem.classList.add("pub-item--first-visible");

    if (currentTopic === "featured") {
      showAllBtn.hidden = false;
      showAllBtn.textContent = "Click to see all publications";
      showLessBtn.hidden = true;
    } else {
      var collapsible =
        currentTopic === "all" && totalMatching > COLLAPSE_LIMIT;
      var needsShowAll = collapsible && !expanded;
      showAllBtn.hidden = !needsShowAll;
      showLessBtn.hidden = !(collapsible && expanded);
      if (needsShowAll) {
        showAllBtn.textContent =
          "Show all publications — " + totalMatching + " in total";
      }
    }
    updateBadges();
  }

  var yearSelect = document.getElementById("filter-year-select");
  var venueSelect = document.getElementById("filter-venue-select");

  function selectTopic(topic) {
    currentTopic = topic;
    expanded = false;
    filterLinks.forEach(function (link) {
      link.classList.toggle(
        "active",
        link.getAttribute("data-topic") === topic,
      );
    });
    if (yearSelect)
      yearSelect.value = topic.indexOf("year:") === 0 ? topic : "";
    if (venueSelect)
      venueSelect.value = topic.indexOf("venue:") === 0 ? topic : "";
    render();
  }

  topicFilter.addEventListener("click", function (e) {
    var link = e.target.closest("a[data-topic]");
    if (!link) return;
    e.preventDefault();
    selectTopic(link.getAttribute("data-topic"));
  });

  pubList.addEventListener("click", function (e) {
    var tag = e.target.closest(".pub-topic");
    if (!tag) return;
    var item = tag.closest(".pub-item");
    var beforeTop = item ? item.getBoundingClientRect().top : null;
    selectTopic(tag.getAttribute("data-topic"));
    if (item && beforeTop !== null) {
      var afterTop = item.getBoundingClientRect().top;
      window.scrollBy(0, afterTop - beforeTop);
    }
  });

  showAllBtn.addEventListener("click", function () {
    if (currentTopic === "featured") {
      selectTopic("all");
    } else {
      expanded = true;
      render();
    }
  });

  showLessBtn.addEventListener("click", function () {
    expanded = false;
    render();
  });

  var expandToggle = document.getElementById("filter-expand-toggle");
  var accordion = document.getElementById("filter-accordion");
  if (expandToggle && accordion) {
    expandToggle.addEventListener("click", function () {
      var isOpen = accordion.hidden;
      accordion.hidden = !isOpen;
      expandToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      expandToggle.textContent = isOpen ? "−" : "+";
    });
  }

  if (yearSelect) {
    yearSelect.addEventListener("change", function () {
      if (yearSelect.value) selectTopic(yearSelect.value);
    });
  }
  if (venueSelect) {
    venueSelect.addEventListener("change", function () {
      if (venueSelect.value) selectTopic(venueSelect.value);
    });
  }

  render();

  function prefetchRemainingThumbs() {
    var urls = pubItems
      .map(function (item) {
        var img = item.querySelector(".pub-thumb img");
        return img ? img.getAttribute("src") : null;
      })
      .filter(Boolean);
    urls.forEach(function (url) {
      var img = new Image();
      img.src = url;
    });
  }

  window.addEventListener("load", function () {
    if ("requestIdleCallback" in window) {
      requestIdleCallback(prefetchRemainingThumbs, { timeout: 5000 });
    } else {
      setTimeout(prefetchRemainingThumbs, 2000);
    }
  });

  // News popover: click/tap is the single open trigger for mouse, touch, and
  // keyboard alike (see the CSS comment on .news-popover-box). Toggling
  // measures and clamps the box's horizontal position so it can't push past
  // the viewport edge and widen the page. Tapping/clicking anywhere outside
  // closes it.
  var newsPopovers = document.querySelectorAll(".news-popover");
  function closeAllPopovers() {
    document.querySelectorAll(".news-popover--open").forEach(function (p) {
      p.classList.remove("news-popover--open");
      var b = p.querySelector(".news-popover-box");
      if (b) b.style.left = "";
    });
  }
  newsPopovers.forEach(function (pop) {
    var trigger = pop.querySelector(".news-popover-trigger");
    var box = pop.querySelector(".news-popover-box");
    if (!trigger || !box) return;
    function toggle() {
      var wasOpen = pop.classList.contains("news-popover--open");
      closeAllPopovers();
      if (wasOpen) return;
      pop.classList.add("news-popover--open");
      var rect = box.getBoundingClientRect();
      var overflowRight = rect.right - (window.innerWidth - 8);
      var shift = overflowRight > 0 ? -overflowRight : 0;
      rect = box.getBoundingClientRect();
      if (rect.left + shift < 8) shift = 8 - rect.left;
      if (shift) box.style.left = shift + "px";
    }
    trigger.addEventListener("click", function (e) {
      e.stopPropagation();
      toggle();
    });
    pop.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        e.stopPropagation();
        toggle();
      }
    });
    box.addEventListener("click", function (e) {
      e.stopPropagation();
    });
  });
  document.addEventListener("click", closeAllPopovers);
})();

(function () {
  var FRAME_COUNT = 51;
  var FRAME_PATH = "static/img/avatar_frames/frame_";
  var images = [];
  var isLoaded = false;
  var currentFrameIndex = -1;

  // Select DOM elements.
  var avatarContainer = document.querySelector(".profile .avatar");
  var avatarImg = avatarContainer ? avatarContainer.querySelector("img") : null;
  var primaryNav = document.querySelector("nav.primary");

  if (!avatarContainer || !avatarImg) return;

  var originalSrc = avatarImg.src;

  window.addEventListener("load", function () {
    var loadedCount = 0;

    for (var i = 0; i < FRAME_COUNT; i++) {
      var img = new Image();
      var frameNum = String(i).padStart(4, "0");
      img.src = FRAME_PATH + frameNum + ".png";

      img.onload = img.onerror = function () {
        loadedCount++;
        if (loadedCount === FRAME_COUNT) {
          isLoaded = true; // Enable scroll interaction only after all 50 frames have loaded.
          updateFrame(); // Reflect the initial scroll position.
        }
      };
      images.push(img);
    }
  });

  function getScrollProgress() {
    var avatarRect = avatarContainer.getBoundingClientRect();
    var navBottom = primaryNav ? primaryNav.getBoundingClientRect().bottom : 0;

    var startY = navBottom;
    var endY = navBottom - avatarRect.height;

    var currentY = avatarRect.top;

    if (currentY > startY) return 0;
    if (currentY < endY) return 1;

    return (startY - currentY) / (startY - endY);
  }

  var lastRenderTime = 0;
  var fpsInterval = 1000 / 60;
  var ticking = false;

  function updateFrame() {
    if (!isLoaded) return;

    var progress = getScrollProgress();

    if (progress <= 0) {
      if (currentFrameIndex !== -1) {
        avatarImg.src = originalSrc;
        currentFrameIndex = -1;
      }
      return;
    }

    var targetIndex = Math.min(
      FRAME_COUNT - 1,
      Math.floor(progress * FRAME_COUNT),
    );

    if (targetIndex !== currentFrameIndex) {
      avatarImg.src = images[targetIndex].src;
      currentFrameIndex = targetIndex;
    }
  }

  window.addEventListener("scroll", function () {
    if (!isLoaded) return;
    if (!ticking) {
      window.requestAnimationFrame(function (currentTime) {
        var elapsed = currentTime - lastRenderTime;
        if (elapsed > fpsInterval) {
          lastRenderTime = currentTime - (elapsed % fpsInterval);
          updateFrame();
        }
        ticking = false;
      });
      ticking = true;
    }
  });
  window.addEventListener("resize", updateFrame);
})();
