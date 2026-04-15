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

  function wireNavToolbar(iframe) {
    var expandBtn = document.getElementById("doc-nav-expand-all");
    var collapseBtn = document.getElementById("doc-nav-collapse-all");
    if (expandBtn) {
      expandBtn.onclick = function () {
        postToNav(iframe, MSG_EXPAND);
      };
    }
    if (collapseBtn) {
      collapseBtn.onclick = function () {
        postToNav(iframe, MSG_COLLAPSE);
      };
    }
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
