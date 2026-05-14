(function () {
  if (typeof window === "undefined") return;

  var style = document.createElement("style");
  style.id = "ecm-nav-active";
  style.textContent =
    '[data-navhref][data-nav-active="true"]{background:#7700FF!important;}' +
    '[data-navhref][data-nav-active="false"]{background:transparent!important;}' +
    '[data-navhref][data-nav-active="true"] p,' +
    '[data-navhref][data-nav-active="true"] span,' +
    '[data-navhref][data-nav-active="true"] svg{color:#FFFFFF!important;}' +
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

  // Intercept Next.js pushState so every navigation triggers applyNav instantly
  var _push = history.pushState.bind(history);
  history.pushState = function () {
    _push.apply(this, arguments);
    requestAnimationFrame(applyNav);
  };

  window.addEventListener("popstate", applyNav);
  applyNav();
  setTimeout(applyNav, 80);
})();
