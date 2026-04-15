/* Shell page: expand/collapse-all via postMessage to nav iframe (reliable vs direct window refs). */
(function () {
  var MSG_EXPAND = "doc-infra-nav-expand-all";
  var MSG_COLLAPSE = "doc-infra-nav-collapse-all";

  function postToNav(iframe, type) {
    var w = iframe.contentWindow;
    if (!w) return;
    try {
      w.postMessage({ type: type }, "*");
    } catch (e) {
      /* ignore */
    }
  }

  function setToggleVisual(btn, pressed) {
    btn.setAttribute("aria-pressed", pressed ? "true" : "false");
    if (pressed) {
      btn.title = "Collapse all sections";
      btn.setAttribute("aria-label", "Collapse all sections");
    } else {
      btn.title = "Expand all sections";
      btn.setAttribute("aria-label", "Expand all sections");
    }
  }

  function wireNavToolbar(iframe) {
    var toggleBtn = document.getElementById("doc-nav-expand-collapse-toggle");
    if (!toggleBtn) return;

    toggleBtn.onclick = function () {
      var pressed = toggleBtn.getAttribute("aria-pressed") === "true";
      if (!pressed) {
        postToNav(iframe, MSG_EXPAND);
        setToggleVisual(toggleBtn, true);
      } else {
        postToNav(iframe, MSG_COLLAPSE);
        setToggleVisual(toggleBtn, false);
      }
    };
  }

  function tryWire(iframe) {
    if (!iframe) return;
    wireNavToolbar(iframe);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var iframe = document.querySelector(".doc-nav-iframe");
    if (!iframe) return;

    function onReady() {
      tryWire(iframe);
    }

    try {
      if (iframe.contentDocument && iframe.contentDocument.readyState === "complete") {
        onReady();
      }
    } catch (e) {
      /* cross-origin or file:// — wait for load */
    }

    iframe.addEventListener("load", onReady);
  });
})();
