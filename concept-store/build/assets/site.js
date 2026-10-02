// The whole of the site's JavaScript. The pages work without it; this adds
// "copy the code" (for pasting into a DM) and the phone's share sheet.
(function () {
  "use strict";

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    // http:// and old WebViews: the textarea route still works
    return new Promise(function (resolve, reject) {
      var t = document.createElement("textarea");
      t.value = text;
      t.setAttribute("readonly", "");
      t.style.position = "fixed";
      t.style.opacity = "0";
      document.body.appendChild(t);
      t.select();
      try { document.execCommand("copy") ? resolve() : reject(); } catch (e) { reject(e); }
      document.body.removeChild(t);
    });
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-copy]");
    if (!b) return;
    var label = b.textContent;
    copyText(b.getAttribute("data-copy")).then(function () {
      b.textContent = "کپی شد — در پیام بچسبانید";
      setTimeout(function () { b.textContent = label; }, 2400);
    }, function () {
      b.textContent = "کپی نشد؛ کد را دستی بنویسید";
    });
  });

  if (navigator.share) {
    document.querySelectorAll(".share").forEach(function (b) {
      b.hidden = false;
      b.addEventListener("click", function () {
        navigator.share({ title: b.getAttribute("data-share-title"), url: location.href })
          .catch(function () {});
      });
    });
  }

  // On a phone the section chips scroll sideways; bring the current one into view.
  var here = document.querySelector(".chips [aria-current]");
  if (here) {
    var row = here.closest("ul");
    if (row.scrollWidth > row.clientWidth) {
      row.scrollLeft += (here.getBoundingClientRect().left + here.offsetWidth / 2) -
                        (row.getBoundingClientRect().left + row.clientWidth / 2);
    }
  }

  // Contact channels not configured yet: the button is drawn, but say so.
  document.querySelectorAll('[data-todo="contact"]').forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); });
  });
})();
