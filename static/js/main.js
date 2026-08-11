/* main.js — shared, site-wide behavior */

(function () {
  "use strict";

  // Auto-dismiss flash alerts after a few seconds
  document.querySelectorAll(".alert").forEach((alertEl) => {
    setTimeout(() => {
      alertEl.style.transition = "opacity .4s ease";
      alertEl.style.opacity = "0";
      setTimeout(() => alertEl.remove(), 400);
    }, 5000);
  });
})();
