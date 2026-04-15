/* Site nav (nav.html in iframe): scroll, branch state, current highlight. Exposes expand/collapse for parent shell. */
(function () {
  var SS_SCROLL = "doc-infra-nav-scroll";
  var SS_OPEN = "doc-infra-nav-open";

  function paramC() {
    try {
      return new URLSearchParams(window.location.search).get("c") || "";
    } catch (e) {
      return "";
    }
  }

  function throttle(fn, ms) {
    var t;
    return function () {
      clearTimeout(t);
      t = setTimeout(fn, ms);
    };
  }

  /** Open every branch that is a prefix of the current manifest path. */
  function mergeAutoExpand(currentPath) {
    if (!currentPath) return;
    document.querySelectorAll(".doc-nav-details[data-nav-path]").forEach(function (el) {
      var p = el.getAttribute("data-nav-path");
      if (!p) return;
      if (currentPath === p || currentPath.indexOf(p + "/") === 0) {
        el.open = true;
      }
    });
  }

  function restoreOpenState() {
    try {
      var raw = sessionStorage.getItem(SS_OPEN);
      if (!raw) return;
      var paths = JSON.parse(raw);
      if (!Array.isArray(paths)) return;
      var set = new Set(paths);
      document.querySelectorAll(".doc-nav-details[data-nav-path]").forEach(function (el) {
        var p = el.getAttribute("data-nav-path");
        if (p && set.has(p)) el.open = true;
      });
    } catch (e) {
      /* ignore */
    }
  }

  function saveOpenState() {
    var paths = [];
    document.querySelectorAll(".doc-nav-details[data-nav-path]").forEach(function (el) {
      var p = el.getAttribute("data-nav-path");
      if (p && el.open) paths.push(p);
    });
    try {
      sessionStorage.setItem(SS_OPEN, JSON.stringify(paths));
    } catch (e) {
      /* ignore */
    }
  }

  function bindToggleListeners() {
    document.querySelectorAll(".doc-nav-details[data-nav-path]").forEach(function (el) {
      el.addEventListener("toggle", saveOpenState);
    });
  }

  /** Highlight the link matching ?c= (manifest path → .html href in nav). */
  function highlightCurrent(manifestPath) {
    if (!manifestPath) return;
    var target = manifestPath.replace(/\.md$/i, ".html");
    document.querySelectorAll(".doc-nav a[href]").forEach(function (a) {
      var href = a.getAttribute("href");
      if (!href) return;
      var norm = href.split("?")[0].split("#")[0];
      if (norm === target) {
        a.classList.add("doc-nav-link--current");
        a.setAttribute("aria-current", "page");
      }
    });
  }

  function expandAllNav() {
    document.querySelectorAll(".doc-nav-details[data-nav-path]").forEach(function (el) {
      el.open = true;
    });
    saveOpenState();
  }

  function collapseAllNav() {
    document.querySelectorAll(".doc-nav-details[data-nav-path]").forEach(function (el) {
      el.open = false;
    });
    mergeAutoExpand(paramC());
    saveOpenState();
  }

  window.docNavExpandAll = expandAllNav;
  window.docNavCollapseAll = collapseAllNav;

  window.addEventListener("message", function (ev) {
    if (ev.source !== window.parent) return;
    var t = ev.data && ev.data.type;
    if (t === "doc-infra-nav-expand-all") expandAllNav();
    else if (t === "doc-infra-nav-collapse-all") collapseAllNav();
  });

  function restoreScroll() {
    try {
      var y = sessionStorage.getItem(SS_SCROLL);
      if (y == null) return;
      var n = parseInt(y, 10);
      if (!isNaN(n)) window.scrollTo(0, n);
    } catch (e) {
      /* ignore */
    }
  }

  function saveScroll() {
    try {
      sessionStorage.setItem(SS_SCROLL, String(window.scrollY || window.pageYOffset));
    } catch (e) {
      /* ignore */
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var c = paramC();
    restoreOpenState();
    mergeAutoExpand(c);
    highlightCurrent(c);
    bindToggleListeners();
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        restoreScroll();
        window.addEventListener("scroll", throttle(saveScroll, 80), { passive: true });
      });
    });
  });
})();
