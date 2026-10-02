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
      b.textContent = "کپی شد — تو پیام بچسبون";
      setTimeout(function () { b.textContent = label; }, 2400);
    }, function () {
      b.textContent = "کپی نشد؛ کد رو دستی بنویس";
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

  // On a phone the section tabs scroll sideways; bring the current one into view.
  var here = document.querySelector(".tabs [aria-current]");
  if (here) {
    var row = here.closest("ul");
    if (row.scrollWidth > row.clientWidth) {
      row.scrollLeft += (here.getBoundingClientRect().left + here.offsetWidth / 2) -
                        (row.getBoundingClientRect().left + row.clientWidth / 2);
    }
  }

  // The phone menu: close it when a link inside is followed (same-page anchors included).
  document.querySelectorAll(".menu a").forEach(function (a) {
    a.addEventListener("click", function () { a.closest("details").open = false; });
  });

  // The verse was sized before the web font arrived and for this window width:
  // size it again when either changes (the picker defines fitVerse inline).
  if (window.fitVerse) {
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(window.fitVerse);
    var ft;
    window.addEventListener("resize", function () { clearTimeout(ft); ft = setTimeout(window.fitVerse, 120); });
  }

  // Dust in the window light: after the entrance, the one thing on the home
  // page that keeps moving. A few warm specks rise and sway in the lit (left)
  // part of the photo and fade at the edges of the light, as in a real
  // sunbeam. Paused off-screen and in a hidden tab; absent with reduced motion.
  (function motes() {
    var c = document.querySelector(".motes");
    if (!c || !c.getContext) return;
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) { c.remove(); return; }
    var ctx = c.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2);
    var W = 0, H = 0, parts = [], running = false, onScreen = true, last = 0;
    var BEAM = 0.6;                       // the light covers the left 60% of the photo

    function spawn(p, anywhere) {
      p.x = W * (0.03 + Math.random() * (BEAM - 0.08));
      p.y = anywhere ? H * (0.1 + Math.random() * 0.8) : H * (0.86 + Math.random() * 0.1);
      p.r = 0.8 + Math.random() * 1.5;
      p.vy = -(4 + Math.random() * 10);   // px per second, rising
      p.vx = (Math.random() - 0.5) * 5;
      p.ph = Math.random() * 6.283;
      p.sp = 0.35 + Math.random() * 0.8;
      p.a = 0.35 + Math.random() * 0.4;
      return p;
    }
    function setup() {
      var r = c.getBoundingClientRect();
      W = r.width; H = r.height;
      c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var n = Math.round(Math.min(48, Math.max(18, W * H / 26000)));
      parts = [];
      for (var i = 0; i < n; i++) parts.push(spawn({}, true));
    }
    function frame(t) {
      if (!running) return;
      var dt = Math.min(0.05, (t - (last || t)) / 1000);
      last = t;
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = "rgb(255, 246, 228)";
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        p.ph += dt * p.sp;
        p.x += (p.vx + Math.sin(p.ph) * 4) * dt;
        p.y += p.vy * dt;
        if (p.y < H * 0.05 || p.x < 0 || p.x > W * BEAM) spawn(p, false);
        var edge = Math.min(1, p.x / (W * 0.08), (W * BEAM - p.x) / (W * 0.14),
                            (p.y - H * 0.05) / (H * 0.12), (H - p.y) / (H * 0.16));
        ctx.globalAlpha = Math.max(0, p.a * edge * (0.65 + 0.35 * Math.sin(p.ph * 2.3)));
        ctx.beginPath();                 // the speck
        ctx.arc(p.x, p.y, p.r, 0, 6.2832);
        ctx.fill();
        ctx.globalAlpha *= 0.1;          // and the faint glow the light gives it
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * 3.2, 0, 6.2832);
        ctx.fill();
      }
      requestAnimationFrame(frame);
    }
    function go() {
      var want = onScreen && !document.hidden;
      if (want && !running) { running = true; last = 0; requestAnimationFrame(frame); }
      if (!want) running = false;
    }
    setup();
    go();
    var t;
    window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(setup, 150); });
    document.addEventListener("visibilitychange", go);
    if (window.IntersectionObserver) {
      new IntersectionObserver(function (e) { onScreen = e[0].isIntersecting; go(); }).observe(c);
    }
  })();

  // Contact channels not configured yet: the button is drawn, but say so.
  document.querySelectorAll('[data-todo="contact"]').forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); });
  });
})();
