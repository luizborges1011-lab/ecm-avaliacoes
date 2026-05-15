(function () {
  if (typeof window === "undefined") return;

  var style = document.createElement("style");
  style.id = "ecm-nav-active";
  style.textContent =
    '[data-navhref][data-nav-active="true"]{background:#7700FF!important;}' +
    '[data-navhref][data-nav-active="false"]{background:transparent!important;}' +
    '[data-navhref][data-nav-active="true"] p,' +
    '[data-navhref][data-nav-active="true"] span,' +
    '[data-navhref][data-nav-active="true"] svg{color:#FFFFFF!important;fill:#FFFFFF!important;}' +
    '[data-navhref][data-nav-active="false"] p,' +
    '[data-navhref][data-nav-active="false"] span,' +
    '[data-navhref][data-nav-active="false"] svg{color:#475569!important;}';
  document.head.appendChild(style);

  function applyNav() {
    var path = window.location.pathname;
    document.querySelectorAll("[data-navhref]").forEach(function (el) {
      el.setAttribute(
        "data-nav-active",
        el.getAttribute("data-navhref") === path ? "true" : "false"
      );
    });
  }

  // Patch pushState and replaceState
  ["pushState", "replaceState"].forEach(function (method) {
    var orig = history[method].bind(history);
    history[method] = function () {
      orig.apply(this, arguments);
      requestAnimationFrame(applyNav);
    };
  });

  window.addEventListener("popstate", applyNav);

  // Re-apply whenever nav items are added/replaced in the DOM (after React re-renders)
  var observer = new MutationObserver(function () {
    if (document.querySelector("[data-navhref]")) {
      applyNav();
    }
  });
  observer.observe(document.body || document.documentElement, {
    childList: true,
    subtree: true,
  });

  // Poll every 300ms as fallback for navigations not caught by pushState patch
  var lastPath = window.location.pathname;
  setInterval(function () {
    if (window.location.pathname !== lastPath) {
      lastPath = window.location.pathname;
      applyNav();
    }
  }, 300);

  applyNav();
  setTimeout(applyNav, 100);
  setTimeout(applyNav, 500);
})();
