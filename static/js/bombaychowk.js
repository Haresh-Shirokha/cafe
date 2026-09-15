// Bombay Chowkk — shared front-end behaviour (vanilla JS, no build step)

// ---------- Splash / intro screen ----------
// Runs immediately (not gated on DOMContentLoaded) so the splash appears
// before the rest of the page is even parsed.
(function () {
  if (document.body) document.body.classList.add("bc-splash-active");
  var MIN_SHOW_MS = 700;
  var start = Date.now();
  function hideSplash() {
    var el = document.getElementById("bc-splash");
    if (!el) return;
    var elapsed = Date.now() - start;
    var wait = Math.max(MIN_SHOW_MS - elapsed, 0);
    setTimeout(function () {
      el.classList.add("bc-splash-hide");
      document.body.classList.remove("bc-splash-active");
      setTimeout(function () { el.remove(); }, 600);
    }, wait);
  }
  if (document.readyState === "complete") {
    hideSplash();
  } else {
    window.addEventListener("load", hideSplash);
  }
})();

document.addEventListener("DOMContentLoaded", function () {
  // ---------- Light/dark theme toggle button(s) ----------
  document.querySelectorAll("[data-bc-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme") || "dark";
      var next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("bc_theme", next);
    });
  });

  // ---------- Mobile nav toggle ----------
  var burger = document.querySelector("[data-bc-burger]");
  var mobileNav = document.querySelector("[data-bc-mobile-nav]");
  if (burger && mobileNav) {
    burger.addEventListener("click", function () {
      mobileNav.classList.toggle("open");
      burger.setAttribute(
        "aria-expanded",
        mobileNav.classList.contains("open") ? "true" : "false"
      );
    });
  }

  // ---------- Desktop dropdown (tap / click, for touch + keyboard support) ----------
  document.querySelectorAll("[data-bc-dropdown]").forEach(function (drop) {
    var trigger = drop.querySelector("[data-bc-dropdown-trigger]");
    if (!trigger) return;
    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      var isOpen = drop.classList.contains("open");
      document.querySelectorAll("[data-bc-dropdown].open").forEach(function (d) {
        d.classList.remove("open");
      });
      if (!isOpen) drop.classList.add("open");
    });
  });
  document.addEventListener("click", function (e) {
    document.querySelectorAll("[data-bc-dropdown].open").forEach(function (d) {
      if (!d.contains(e.target)) d.classList.remove("open");
    });
  });

  // ---------- Admin sidebar (mobile toggle) ----------
  var sidebar = document.querySelector("[data-bc-admin-sidebar]");
  var overlay = document.querySelector("[data-bc-admin-overlay]");
  var openBtn = document.querySelector("[data-bc-admin-sidebar-open]");
  var closeBtn = document.querySelector("[data-bc-admin-sidebar-close]");
  function openSidebar() {
    if (sidebar) sidebar.classList.add("open");
    if (overlay) overlay.classList.add("open");
  }
  function closeSidebar() {
    if (sidebar) sidebar.classList.remove("open");
    if (overlay) overlay.classList.remove("open");
  }
  if (openBtn) openBtn.addEventListener("click", openSidebar);
  if (closeBtn) closeBtn.addEventListener("click", closeSidebar);
  if (overlay) overlay.addEventListener("click", closeSidebar);

  // ---------- Admin sidebar (desktop hide/show, remembered) ----------
  var shell = document.querySelector("[data-bc-admin-shell]");
  var hideToggle = document.querySelector("[data-bc-admin-sidebar-hide-toggle]");
  var hideLabel = document.querySelector("[data-bc-admin-hide-label]");
  if (shell && hideToggle) {
    var HIDE_KEY = "bc_admin_sidebar_hidden";
    function applyHiddenState(hidden) {
      shell.classList.toggle("sidebar-hidden", hidden);
      if (hideLabel) hideLabel.textContent = hidden ? "Show menu" : "Hide menu";
    }
    applyHiddenState(localStorage.getItem(HIDE_KEY) === "1");
    hideToggle.addEventListener("click", function () {
      var nowHidden = !shell.classList.contains("sidebar-hidden");
      applyHiddenState(nowHidden);
      localStorage.setItem(HIDE_KEY, nowHidden ? "1" : "0");
    });
  }

  // ---------- Dismissible alerts ----------
  document.querySelectorAll("[data-bc-alert-close]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var alertEl = btn.closest(".bc-alert");
      if (alertEl) alertEl.remove();
    });
  });

  // ---------- Weekly-events day tabs ----------
  var dayButtons = document.querySelectorAll("[data-bc-event-day]");
  var panels = document.querySelectorAll("[data-bc-event-panel]");
  var eventSelect = document.querySelector("[data-bc-rsvp-event-select]");
  if (dayButtons.length) {
    dayButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var idx = btn.getAttribute("data-bc-event-day");
        dayButtons.forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        panels.forEach(function (p) {
          p.style.display = p.getAttribute("data-bc-event-panel") === idx ? "" : "none";
        });
        if (eventSelect) {
          var title = btn.getAttribute("data-bc-event-title");
          if (title) eventSelect.value = title;
        }
      });
    });
  }

  // ---------- Partner-type picker (writes into the hidden/real select) ----------
  var partnerButtons = document.querySelectorAll("[data-bc-partner-type]");
  var partnerSelect = document.querySelector("[data-bc-partner-select]");
  if (partnerButtons.length && partnerSelect) {
    partnerButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var val = btn.getAttribute("data-bc-partner-type");
        partnerSelect.value = val;
        partnerButtons.forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
      });
    });
  }

  // ---------- Live "time since order placed" timer ----------
  function formatElapsed(ms) {
    if (ms < 0) ms = 0;
    var totalSec = Math.floor(ms / 1000);
    var h = Math.floor(totalSec / 3600);
    var m = Math.floor((totalSec % 3600) / 60);
    var s = totalSec % 60;
    var parts = [];
    if (h > 0) parts.push(h + "h");
    parts.push(m + "m");
    parts.push(s + "s");
    return parts.join(" ");
  }
  function updateOrderTimers() {
    document.querySelectorAll(".order-timer").forEach(function (el) {
      var created = new Date(el.dataset.created);
      var now = new Date();
      el.textContent = formatElapsed(now - created) + " ago";
    });
  }
  updateOrderTimers();
  setInterval(updateOrderTimers, 1000);
});
