(function () {
  'use strict';

  var GITHUB_API = 'https://api.github.com';
  var CACHE_TTL = 10 * 60 * 1000;

  // ── Utilities ──────────────────────────────────────────────
  function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qsa(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

  function relativeTime(dateStr) {
    var now = Date.now();
    var d = new Date(dateStr).getTime();
    var diff = now - d;
    var sec = Math.floor(diff / 1000);
    if (sec < 60) return sec + '초 전';
    var min = Math.floor(sec / 60);
    if (min < 60) return min + '분 전';
    var hr = Math.floor(min / 60);
    if (hr < 24) return hr + '시간 전';
    var day = Math.floor(hr / 24);
    if (day < 30) return day + '일 전';
    var mon = Math.floor(day / 30);
    if (mon < 12) return mon + '개월 전';
    return Math.floor(mon / 12) + '년 전';
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ── Reading Progress Bar ───────────────────────────────────
  function initProgressBar() {
    var bar = qs('#docProgressBar');
    if (!bar) return;
    var body = qs('#docArticleBody');
    if (!body) return;

    function update() {
      var rect = body.getBoundingClientRect();
      var bodyTop = rect.top + window.scrollY;
      var bodyHeight = rect.height;
      var scrolled = window.scrollY - bodyTop;
      var pct = Math.min(100, Math.max(0, (scrolled / (bodyHeight - window.innerHeight)) * 100));
      bar.style.width = pct + '%';
    }

    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  // ── Word Count & Reading Time ──────────────────────────────
  function initWordCount() {
    var body = qs('#docArticleBody');
    if (!body) return;

    var text = (body.textContent || body.innerText || '').trim();
    var koreanChars = (text.match(/[\uAC00-\uD7A3]/g) || []).length;
    var latinWords = text.replace(/[\uAC00-\uD7A3]/g, ' ').split(/\s+/).filter(function (w) { return w.length > 0; }).length;
    var totalWords = koreanChars + latinWords;
    var readMin = Math.max(1, Math.ceil(totalWords / 250));

    var metaWords = qs('#docMetaWords span');
    if (metaWords) metaWords.textContent = totalWords.toLocaleString() + ' 단어';

    var metaRead = qs('#docMetaReadTime span');
    if (metaRead) metaRead.textContent = '약 ' + readMin + '분';

    var infoWords = qs('#docInfoWords dd');
    if (infoWords) infoWords.textContent = totalWords.toLocaleString();

    var infoRead = qs('#docInfoRead dd');
    if (infoRead) infoRead.textContent = '약 ' + readMin + '분';
  }

  // ── Table of Contents ──────────────────────────────────────
  function initToc() {
    var body = qs('#docArticleBody');
    var list = qs('#docTocList');
    if (!body || !list) return;

    var headings = qsa('h1, h2, h3, h4', body);
    if (headings.length === 0) {
      var tocBox = qs('#docTocBox');
      if (tocBox) tocBox.style.display = 'none';
      return;
    }

    var minLevel = 6;
    headings.forEach(function (h) {
      var lvl = parseInt(h.tagName.charAt(1), 10);
      if (lvl < minLevel) minLevel = lvl;
    });

    var filtered = headings.filter(function (h) {
      var lvl = parseInt(h.tagName.charAt(1), 10);
      return lvl <= minLevel + 2;
    });

    filtered.forEach(function (h, i) {
      if (!h.id) h.id = 'doc-heading-' + i;
      var lvl = parseInt(h.tagName.charAt(1), 10);
      var li = document.createElement('li');
      li.className = 'toc-h' + lvl;
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var top = h.getBoundingClientRect().top + window.scrollY - 100;
        window.scrollTo({ top: top, behavior: 'smooth' });
        history.pushState(null, '', '#' + h.id);
      });
      li.appendChild(a);
      list.appendChild(li);
    });

    // Scroll spy
    var links = qsa('a', list);
    var ticking = false;

    function updateActive() {
      var scrollPos = window.scrollY + 120;
      var active = filtered[0];
      for (var i = filtered.length - 1; i >= 0; i--) {
        if (filtered[i].getBoundingClientRect().top + window.scrollY <= scrollPos) {
          active = filtered[i];
          break;
        }
      }
      links.forEach(function (l) {
        l.classList.toggle('active', l.getAttribute('href') === '#' + active.id);
      });
    }

    window.addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(function () {
          updateActive();
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });

    setTimeout(updateActive, 200);
  }

  // ── Tabs ───────────────────────────────────────────────────
  function initTabs() {
    var tabs = qsa('.doc-tab');
    var panels = qsa('.doc-tab-panel');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        var target = tab.getAttribute('data-tab');
        tabs.forEach(function (t) { t.classList.toggle('active', t === tab); });
        panels.forEach(function (p) {
          p.classList.toggle('active', p.id === 'tab' + target.charAt(0).toUpperCase() + target.slice(1));
        });
      });
    });
  }

  // ── Mobile Sidebar ─────────────────────────────────────────
  function initSidebar() {
    var sidebar = qs('#docSidebarLeft');
    var openBtn = qs('#docMobileSidebarBtn');
    var closeBtn = qs('#docSidebarCloseBtn');
    var overlay = qs('#docOverlay');
    var mTbSidebar = qs('#docMTbSidebar');

    function openSidebar() {
      if (sidebar) sidebar.classList.add('open');
      if (overlay) overlay.classList.add('show');
      document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
      if (sidebar) sidebar.classList.remove('open');
      if (overlay) overlay.classList.remove('show');
      document.body.style.overflow = '';
    }

    if (openBtn) openBtn.addEventListener('click', openSidebar);
    if (mTbSidebar) mTbSidebar.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if (overlay) overlay.addEventListener('click', function () {
      closeSidebar();
      closeMobileToc();
    });

    // Swipe-to-open from left edge
    var touchStartX = 0;
    var touchStartY = 0;
    var swiping = false;

    document.addEventListener('touchstart', function (e) {
      var x = e.touches[0].clientX;
      if (x < 24 && !sidebar.classList.contains('open')) {
        touchStartX = x;
        touchStartY = e.touches[0].clientY;
        swiping = true;
      }
    }, { passive: true });

    document.addEventListener('touchmove', function (e) {
      if (!swiping) return;
      var dx = e.touches[0].clientX - touchStartX;
      var dy = Math.abs(e.touches[0].clientY - touchStartY);
      if (dy > 40) { swiping = false; return; }
      if (dx > 60) {
        swiping = false;
        openSidebar();
      }
    }, { passive: true });

    document.addEventListener('touchend', function () { swiping = false; }, { passive: true });
  }

  // ── Mobile TOC Bottom Sheet ────────────────────────────────
  function initMobileToc() {
    var sheet = qs('#docMobileTocSheet');
    var closeBtn = qs('#docMobileTocClose');
    var tocBtn = qs('#docMTbToc');
    var overlay = qs('#docOverlay');
    var mobileTocList = qs('#docMobileTocList');

    if (!sheet) return;

    if (tocBtn) tocBtn.addEventListener('click', openMobileToc);
    if (closeBtn) closeBtn.addEventListener('click', closeMobileToc);

    var handle = qs('#docMobileTocHandle');
    if (handle) {
      var startY = 0;
      handle.addEventListener('touchstart', function (e) {
        startY = e.touches[0].clientY;
      }, { passive: true });
      handle.addEventListener('touchmove', function (e) {
        var dy = e.touches[0].clientY - startY;
        if (dy > 80) closeMobileToc();
      }, { passive: true });
    }

    // Populate mobile TOC from the same headings
    var body = qs('#docArticleBody');
    if (!body || !mobileTocList) return;

    var headings = qsa('h1, h2, h3, h4', body);
    if (headings.length === 0) return;

    var minLevel = 6;
    headings.forEach(function (h) {
      var lvl = parseInt(h.tagName.charAt(1), 10);
      if (lvl < minLevel) minLevel = lvl;
    });

    var filtered = headings.filter(function (h) {
      return parseInt(h.tagName.charAt(1), 10) <= minLevel + 2;
    });

    filtered.forEach(function (h, i) {
      if (!h.id) h.id = 'doc-heading-' + i;
      var lvl = parseInt(h.tagName.charAt(1), 10);
      var li = document.createElement('li');
      li.className = 'toc-h' + lvl;
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      a.addEventListener('click', function (e) {
        e.preventDefault();
        closeMobileToc();
        setTimeout(function () {
          var top = h.getBoundingClientRect().top + window.scrollY - 60;
          window.scrollTo({ top: top, behavior: 'smooth' });
        }, 200);
      });
      li.appendChild(a);
      mobileTocList.appendChild(li);
    });

    // Sync active state with scroll
    var mobileLinks = qsa('a', mobileTocList);
    function syncMobileActive() {
      var scrollPos = window.scrollY + 120;
      var active = filtered[0];
      for (var i = filtered.length - 1; i >= 0; i--) {
        if (filtered[i].getBoundingClientRect().top + window.scrollY <= scrollPos) {
          active = filtered[i];
          break;
        }
      }
      mobileLinks.forEach(function (l) {
        l.classList.toggle('active', l.getAttribute('href') === '#' + active.id);
      });
    }

    window.addEventListener('scroll', function () {
      requestAnimationFrame(syncMobileActive);
    }, { passive: true });
  }

  function openMobileToc() {
    var sheet = qs('#docMobileTocSheet');
    var overlay = qs('#docOverlay');
    if (sheet) sheet.classList.add('open');
    if (overlay) overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeMobileToc() {
    var sheet = qs('#docMobileTocSheet');
    var overlay = qs('#docOverlay');
    if (sheet) sheet.classList.remove('open');
    if (overlay) overlay.classList.remove('show');
    document.body.style.overflow = '';
  }

  // ── Mobile: Back to Top ────────────────────────────────────
  function initBackToTop() {
    var btn = qs('#docMTbTop');
    if (!btn) return;
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ── Mobile: Theme Toggle ───────────────────────────────────
  function initMobileThemeToggle() {
    var btn = qs('#docMTbTheme');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var html = document.documentElement;
      var current = html.getAttribute('data-theme') || 'light';
      var next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      var themeInput = qs('#themeToggleInput');
      if (themeInput) themeInput.checked = next === 'dark';
      var icon = btn.querySelector('svg');
      if (icon) {
        icon.innerHTML = next === 'dark'
          ? '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>'
          : '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
      }
    });
  }

  // ── Auto-hide header on scroll ─────────────────────────────
  function initScrollHeader() {
    var header = qs('.site-header');
    var tabBar = qs('.doc-tab-bar');
    if (!header) return;

    var lastScrollY = 0;
    var ticking = false;
    var threshold = 60;

    function onScroll() {
      var currentY = window.scrollY;
      if (currentY > lastScrollY && currentY > threshold) {
        header.classList.add('header-hidden');
        if (tabBar) tabBar.classList.remove('tab-bar-shifted');
      } else {
        header.classList.remove('header-hidden');
        if (tabBar) tabBar.classList.add('tab-bar-shifted');
      }
      lastScrollY = currentY;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(function () {
          onScroll();
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });

    // Initial state
    if (tabBar) tabBar.classList.add('tab-bar-shifted');
  }

  // ── Scroll hint for overflowing elements ───────────────────
  function initScrollHints() {
    if (window.innerWidth > 768) return;
    var codeBlocks = qsa('.doc-article-body pre code, .doc-article-body table');
    codeBlocks.forEach(function (el) {
      if (el.scrollWidth > el.clientWidth + 8) {
        var hint = document.createElement('span');
        hint.className = 'doc-scroll-hint visible';
        hint.textContent = '← 스크롤 →';
        el.closest('pre, table')?.parentElement?.style && (el.closest('pre') || el.closest('.doc-article-body')).appendChild(hint);
      }
    });
  }

  // ── Document Search (sidebar) ──────────────────────────────
  function initSearch() {
    var input = qs('#docSearchInput');
    if (!input) return;
    var items = qsa('.doc-nav-item');

    input.addEventListener('input', function () {
      var q = input.value.toLowerCase().trim();
      items.forEach(function (item) {
        var link = item.querySelector('.doc-nav-link-text');
        var text = (link ? link.textContent : item.textContent).toLowerCase();
        item.style.display = text.includes(q) || q === '' ? '' : 'none';
      });

      qsa('.doc-nav-group').forEach(function (group) {
        var visibleItems = group.querySelectorAll('.doc-nav-item[style=""],.doc-nav-item:not([style])');
        var hasVisible = false;
        visibleItems.forEach(function (i) {
          if (i.style.display !== 'none') hasVisible = true;
        });
        group.style.display = hasVisible || q === '' ? '' : 'none';
      });
    });
  }

  // ── Print ──────────────────────────────────────────────────
  function initPrint() {
    var btn = qs('#docPrintBtn');
    if (btn) btn.addEventListener('click', function () { window.print(); });
  }

  // ── Copy Source ────────────────────────────────────────────
  function initCopySource() {
    var btn = qs('#docCopySourceBtn');
    var code = qs('#docSourceCode');
    if (!btn || !code) return;

    btn.addEventListener('click', function () {
      navigator.clipboard.writeText(code.textContent).then(function () {
        btn.classList.add('copied');
        var span = btn.querySelector('span');
        if (span) span.textContent = '복사됨';
        setTimeout(function () {
          btn.classList.remove('copied');
          if (span) span.textContent = '복사';
        }, 2000);
      });
    });
  }

  // ── GitHub API: Commit History ─────────────────────────────
  function initGitHistory() {
    var viewer = qs('.doc-viewer');
    if (!viewer) return;

    var repo = viewer.getAttribute('data-github-repo');
    var filePath = viewer.getAttribute('data-github-path');
    if (!repo || !filePath) {
      showHistoryEmpty('github_path가 설정되지 않았습니다.');
      showRecentEmpty();
      return;
    }

    var cacheKey = 'doc_commits_' + repo + '_' + filePath;
    var cached = sessionStorage.getItem(cacheKey);
    if (cached) {
      try {
        var parsed = JSON.parse(cached);
        if (Date.now() - parsed.ts < CACHE_TTL) {
          renderCommits(parsed.data);
          renderRecentChanges(parsed.data);
          return;
        }
      } catch (e) { /* ignore */ }
    }

    var url = GITHUB_API + '/repos/' + repo + '/commits?path=' + encodeURIComponent(filePath) + '&per_page=30';
    fetch(url, { headers: { Accept: 'application/vnd.github.v3+json' } })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        sessionStorage.setItem(cacheKey, JSON.stringify({ ts: Date.now(), data: data }));
        renderCommits(data);
        renderRecentChanges(data);
      })
      .catch(function (err) {
        console.warn('GitHub API error:', err);
        showHistoryEmpty('커밋 히스토리를 불러오지 못했습니다. (' + err.message + ')');
        showRecentEmpty();
      });
  }

  function renderCommits(commits) {
    var container = qs('#docGitTimeline');
    if (!container) return;

    if (!commits || commits.length === 0) {
      showHistoryEmpty('이 파일에 대한 커밋이 없습니다.');
      return;
    }

    container.innerHTML = '';

    commits.forEach(function (c) {
      var author = c.author || {};
      var commitInfo = c.commit || {};
      var authorInfo = commitInfo.author || {};

      var el = document.createElement('div');
      el.className = 'doc-commit';

      var avatarUrl = author.avatar_url || 'https://github.githubassets.com/images/gravatars/gravatar-user-420.png';
      var login = author.login || authorInfo.name || 'unknown';
      var message = (commitInfo.message || '').split('\n')[0];
      var date = authorInfo.date || '';
      var sha = (c.sha || '').substring(0, 7);
      var commitUrl = 'https://github.com/' + qs('.doc-viewer').getAttribute('data-github-repo') + '/commit/' + c.sha;

      el.innerHTML =
        '<img class="doc-commit-avatar" src="' + escapeHtml(avatarUrl) + '" alt="" loading="lazy">' +
        '<div class="doc-commit-body">' +
          '<p class="doc-commit-message">' + escapeHtml(message) + '</p>' +
          '<div class="doc-commit-meta">' +
            '<span class="doc-commit-author">' + escapeHtml(login) + '</span>' +
            '<span>' + relativeTime(date) + '</span>' +
            '<a class="doc-commit-sha" href="' + escapeHtml(commitUrl) + '" target="_blank" rel="noopener">' + sha + '</a>' +
          '</div>' +
          '<button class="doc-diff-toggle" data-sha="' + c.sha + '">변경 내용 보기 ▾</button>' +
          '<div class="doc-diff-content" id="diff-' + c.sha + '"></div>' +
        '</div>';

      container.appendChild(el);

      var toggleBtn = el.querySelector('.doc-diff-toggle');
      toggleBtn.addEventListener('click', function () {
        var panel = qs('#diff-' + c.sha);
        if (panel.classList.contains('show')) {
          panel.classList.remove('show');
          toggleBtn.textContent = '변경 내용 보기 ▾';
          return;
        }
        toggleBtn.textContent = '접기 ▴';
        panel.classList.add('show');
        if (panel.children.length > 0) return;
        loadDiff(c.sha, panel);
      });
    });
  }

  function loadDiff(sha, container) {
    var repo = qs('.doc-viewer').getAttribute('data-github-repo');
    var filePath = qs('.doc-viewer').getAttribute('data-github-path');

    container.innerHTML = '<div class="doc-history-placeholder"><div class="doc-loading-spinner"></div></div>';

    fetch(GITHUB_API + '/repos/' + repo + '/commits/' + sha, {
      headers: { Accept: 'application/vnd.github.v3+json' }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var files = data.files || [];
        var targetFile = null;
        for (var i = 0; i < files.length; i++) {
          if (files[i].filename === filePath || files[i].filename.endsWith('/' + filePath.split('/').pop())) {
            targetFile = files[i];
            break;
          }
        }

        if (!targetFile || !targetFile.patch) {
          container.innerHTML = '<p style="padding:12px;font-size:0.8125rem;color:var(--text-secondary);">이 커밋에서 해당 파일의 변경 내용을 찾을 수 없습니다.</p>';
          return;
        }

        var stats = (data.stats || {});
        var statsHtml = '<div class="doc-commit-stats" style="padding:8px 12px;border-bottom:1px solid var(--border-color)">' +
          '<span class="doc-stat-add">+' + (targetFile.additions || 0) + '</span>' +
          '<span class="doc-stat-del">-' + (targetFile.deletions || 0) + '</span>' +
          '</div>';

        container.innerHTML = '<div class="doc-diff-panel">' + statsHtml + renderPatch(targetFile.patch) + '</div>';
      })
      .catch(function () {
        container.innerHTML = '<p style="padding:12px;font-size:0.8125rem;color:var(--text-secondary);">변경 내용을 불러오지 못했습니다.</p>';
      });
  }

  function renderPatch(patch) {
    if (!patch) return '';
    var lines = patch.split('\n');
    var html = '<table class="doc-diff-table">';
    var oldNum = 0;
    var newNum = 0;

    lines.forEach(function (line) {
      var hunkMatch = line.match(/^@@\s*-(\d+)(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s*@@(.*)/);
      if (hunkMatch) {
        oldNum = parseInt(hunkMatch[1], 10) - 1;
        newNum = parseInt(hunkMatch[2], 10) - 1;
        html += '<tr class="doc-diff-line doc-diff-hunk"><td class="doc-diff-line-num"></td><td class="doc-diff-line-num"></td><td class="doc-diff-line-content">' + escapeHtml(line) + '</td></tr>';
        return;
      }

      if (line.startsWith('+')) {
        newNum++;
        html += '<tr class="doc-diff-line doc-diff-add"><td class="doc-diff-line-num"></td><td class="doc-diff-line-num">' + newNum + '</td><td class="doc-diff-line-content">' + escapeHtml(line) + '</td></tr>';
      } else if (line.startsWith('-')) {
        oldNum++;
        html += '<tr class="doc-diff-line doc-diff-del"><td class="doc-diff-line-num">' + oldNum + '</td><td class="doc-diff-line-num"></td><td class="doc-diff-line-content">' + escapeHtml(line) + '</td></tr>';
      } else {
        oldNum++;
        newNum++;
        html += '<tr class="doc-diff-line"><td class="doc-diff-line-num">' + oldNum + '</td><td class="doc-diff-line-num">' + newNum + '</td><td class="doc-diff-line-content">' + escapeHtml(line) + '</td></tr>';
      }
    });

    html += '</table>';
    return html;
  }

  function renderRecentChanges(commits) {
    var list = qs('#docRecentList');
    if (!list) return;

    if (!commits || commits.length === 0) {
      showRecentEmpty();
      return;
    }

    list.innerHTML = '';
    var shown = commits.slice(0, 5);
    shown.forEach(function (c) {
      var commitInfo = c.commit || {};
      var authorInfo = commitInfo.author || {};
      var message = (commitInfo.message || '').split('\n')[0];
      var date = authorInfo.date || '';

      var item = document.createElement('div');
      item.className = 'doc-recent-item';
      item.innerHTML =
        '<span class="doc-recent-item-message" title="' + escapeHtml(message) + '">' + escapeHtml(message) + '</span>' +
        '<span class="doc-recent-item-meta">' +
          '<span>' + relativeTime(date) + '</span>' +
        '</span>';
      list.appendChild(item);
    });
  }

  function showHistoryEmpty(msg) {
    var container = qs('#docGitTimeline');
    if (!container) return;
    container.innerHTML =
      '<div class="doc-history-empty">' +
        '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' +
        '<p>' + escapeHtml(msg) + '</p>' +
      '</div>';
  }

  function showRecentEmpty() {
    var list = qs('#docRecentList');
    if (list) list.innerHTML = '<span class="doc-recent-loading">변경 이력 없음</span>';
  }

  // ── Listing page search ────────────────────────────────────
  function initListingSearch() {
    var input = qs('#docsListingSearch');
    if (!input) return;
    var cards = qsa('.docs-card');
    var groups = qsa('.docs-listing-group');

    input.addEventListener('input', function () {
      var q = input.value.toLowerCase().trim();
      cards.forEach(function (card) {
        var title = (card.querySelector('.docs-card-title') || {}).textContent || '';
        var desc = (card.querySelector('.docs-card-desc') || {}).textContent || '';
        var match = title.toLowerCase().includes(q) || desc.toLowerCase().includes(q) || q === '';
        card.style.display = match ? '' : 'none';
      });
      groups.forEach(function (g) {
        var visibleCards = g.querySelectorAll('.docs-card:not([style*="none"])');
        g.style.display = visibleCards.length > 0 || q === '' ? '' : 'none';
      });
    });
  }

  // ── Initialize ─────────────────────────────────────────────
  function init() {
    initProgressBar();
    initWordCount();
    initToc();
    initTabs();
    initSidebar();
    initMobileToc();
    initBackToTop();
    initMobileThemeToggle();
    initScrollHeader();
    initSearch();
    initPrint();
    initCopySource();
    initGitHistory();
    initListingSearch();
    initScrollHints();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
