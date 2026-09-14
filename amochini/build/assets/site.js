/* آموچینی — amochini.ir
   No framework, no third-party requests. Everything degrades to working HTML:
   the nav is a list of real links, the finder is a real <form> with a real
   action, and every product card is a real <a href>. JS only makes it faster. */
(function () {
  'use strict';

  /* ---------- Persian text normalisation ----------------------------------
     Iranian keyboards and copy-pasted text mix Arabic and Persian codepoints.
     Without folding, a user typing Arabic ي (U+064A) gets zero results for a
     product stored with Persian ی (U+06CC). ZWNJ becomes a SPACE rather than
     being deleted: deleting it turns "ام‌وی‌ام" into "امویام", which still
     fails to match "ام وی ام"; converting to space makes both agree. */
  var FOLD = {
    'ي': 'ی', 'ى': 'ی', 'ے': 'ی', 'ئ': 'ی',        // yeh family  -> ی
    'ك': 'ک', 'ڪ': 'ک',                              // kaf family  -> ک
    'ة': 'ه', 'ۀ': 'ه', 'ہ': 'ه',                    // heh family  -> ه
    'آ': 'ا', 'أ': 'ا', 'إ': 'ا', 'ٱ': 'ا',          // alef family -> ا
    'ؤ': 'و',
    'ـ': ''                                          // tatweel: drop
  };
  // Iranians routinely write a Latin model letter out phonetically —
  // "چری تی ۵" is Chery T5, "ترا ایکس" is TRA-X. Applied to the QUERY only,
  // never to the stored index, so it can never corrupt product data.
  var LETTER_NAMES = {
    'ایکس': 'x', 'اکس': 'x', 'اس': 's', 'بی': 'b', 'سی': 'c', 'دی': 'd',
    'ای': 'e', 'جی': 'g', 'اچ': 'h', 'کی': 'k', 'ام': 'm', 'ان': 'n',
    'او': 'o', 'پی': 'p', 'آر': 'r', 'ار': 'r', 'تی': 't', 'وی': 'v',
    'زد': 'z', 'جی\u200Cای': 'j'
  };
  function expandLetterNames(q) {
    return q.split(' ').map(function (w) {
      return LETTER_NAMES.hasOwnProperty(w) ? LETTER_NAMES[w] : w;
    }).join(' ');
  }
  function norm(s) {
    if (!s) return '';
    s = String(s);
    var out = '';
    for (var i = 0; i < s.length; i++) {
      var c = s[i], cc = s.charCodeAt(i);
      if (FOLD.hasOwnProperty(c)) { out += FOLD[c]; continue; }
      if (cc >= 0x06F0 && cc <= 0x06F9) { out += String(cc - 0x06F0); continue; } // ۰-۹
      if (cc >= 0x0660 && cc <= 0x0669) { out += String(cc - 0x0660); continue; } // ٠-٩
      if (cc === 0x200C || cc === 0x200D) { out += ' '; continue; }               // ZWNJ/ZWJ
      out += c;
    }
    return out.replace(/[^\w؀-ۿ]+/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
  }

  function faDigits(n) {
    return String(n).replace(/\d/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'[+d]; });
  }
  function toman(rial) {
    return faDigits((rial / 10).toLocaleString('en-US')).replace(/,/g, '،');
  }

  /* ---------- mobile nav ------------------------------------------------- */
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.getElementById('mainnav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('open', !open);
    });
  }

  /* ---------- site search with suggestions -------------------------------
     The index is fetched lazily on first interaction so it never competes
     with the page's own render. */
  var INDEX = null, indexPromise = null;
  function loadIndex() {
    if (indexPromise) return indexPromise;
    indexPromise = fetch('/search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (d) { INDEX = d; return d; })
      .catch(function () { INDEX = []; return []; });
    return indexPromise;
  }

  function score(item, q) {
    var hay = item.k;
    if (hay.indexOf(q) === -1) {
      var parts = q.split(' ');
      for (var i = 0; i < parts.length; i++) {
        if (parts[i] && hay.indexOf(parts[i]) === -1) return -1;
      }
      return 1;
    }
    return hay.indexOf(q) === 0 ? 3 : 2;
  }

  function search(q, limit) {
    q = expandLetterNames(norm(q));
    if (!q || !INDEX) return [];
    var hits = [];
    for (var i = 0; i < INDEX.length; i++) {
      var s = score(INDEX[i], q);
      if (s > 0) hits.push([s, INDEX[i]]);
    }
    hits.sort(function (a, b) { return b[0] - a[0]; });
    return hits.slice(0, limit || 8).map(function (h) { return h[1]; });
  }

  var input = document.getElementById('q-top');
  var box = document.getElementById('suggest');
  if (input && box) {
    var t;
    input.addEventListener('input', function () {
      clearTimeout(t);
      t = setTimeout(function () {
        var q = input.value.trim();
        if (q.length < 2) { box.classList.remove('open'); box.innerHTML = ''; return; }
        loadIndex().then(function () {
          var hits = search(q, 8);
          if (!hits.length) {
            box.innerHTML = '<p class="s-none">نتیجه‌ای پیدا نشد</p>';
          } else {
            box.innerHTML = hits.map(function (h) {
              return '<a href="' + h.u + '">' + h.t +
                '<span class="s-price"> — ' +
                (h.p ? toman(h.p) + ' تومان' : 'استعلام قیمت') + '</span></a>';
            }).join('');
          }
          box.classList.add('open');
        });
      }, 120);
    });
    input.addEventListener('focus', loadIndex);
    document.addEventListener('click', function (ev) {
      if (!box.contains(ev.target) && ev.target !== input) box.classList.remove('open');
    });
    input.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') box.classList.remove('open');
    });
  }

  /* ---------- home vehicle finder ----------------------------------------
     Submits to the right category page carrying the brand/axle as query
     params, which the category filter below reads on load. */
  var finder = document.getElementById('finder');
  if (finder) {
    finder.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var brand = finder.querySelector('#f-brand').value;
      var cat = finder.querySelector('#f-cat').value || 'brake-pads';
      var axle = finder.querySelector('#f-axle').value;
      var qs = [];
      if (brand) qs.push('brand=' + encodeURIComponent(brand));
      if (axle) qs.push('axle=' + encodeURIComponent(axle));
      location.href = '/' + cat + '/' + (qs.length ? '?' + qs.join('&') : '');
    });
  }

  /* ---------- product slider ---------------------------------------------
     The track is a native scroll-snap container; this only adds the arrows,
     the progress rail and keyboard paging.

     RTL is the whole difficulty here. In a dir=rtl scroller the WHATWG
     behaviour (Chrome 85+, Firefox, Safari 15.2+) is that scrollLeft starts
     at 0 at the RIGHT edge and goes NEGATIVE moving left. Older WebKit went
     from a positive max down to 0 instead. Rather than sniff, we measure:
     `maxScroll` is derived from scrollWidth, and positions are normalised
     through Math.abs, so both conventions land on the same 0..1 progress. */
  [].forEach.call(document.querySelectorAll('.slider'), function (root) {
    var track = root.querySelector('.slider-track');
    var nav   = root.querySelector('.slider-nav');
    var rail  = root.querySelector('.slider-rail');
    var fill  = root.querySelector('.slider-fill');
    if (!track) return;

    var prev = root.querySelector('.s-prev');
    var next = root.querySelector('.s-next');

    function maxScroll() { return track.scrollWidth - track.clientWidth; }
    function pos() { return Math.abs(track.scrollLeft); }

    // One "page" is a whole viewport of cards minus a sliver, so the user
    // keeps a visual anchor between pages instead of jumping blind.
    function step() {
      var card = track.querySelector('.card');
      var w = card ? card.getBoundingClientRect().width + 16 : 240;
      return Math.max(w, Math.floor(track.clientWidth / w) * w - w * 0.25);
    }

    // Direction is resolved from the computed style, not assumed, so this
    // keeps working if the document is ever rendered LTR.
    var rtl = getComputedStyle(track).direction === 'rtl';
    function go(forward) {
      var delta = step() * (forward ? 1 : -1) * (rtl ? -1 : 1);
      track.scrollBy({ left: delta, behavior: 'smooth' });
    }

    function update() {
      var max = maxScroll();
      var overflowing = max > 2;
      if (nav) nav.hidden = !overflowing;
      if (rail) rail.hidden = !overflowing;
      if (!overflowing) { root.removeAttribute('data-overflow'); return; }

      var p = pos();
      var atStart = p <= 2;
      var atEnd = p >= max - 2;
      if (prev) prev.disabled = atStart;
      if (next) next.disabled = atEnd;
      root.setAttribute('data-overflow',
        atStart ? 'end' : atEnd ? 'start' : 'both');

      if (fill) {
        // Width = the share of the track currently on screen.
        // Offset = how far through the scroll we are, as a share of the
        // remaining rail. Expressed as inset-inline-start so the browser
        // flips it for RTL and there is no direction maths here at all.
        var visible = Math.min(1, track.clientWidth / track.scrollWidth) * 100;
        var progress = max ? p / max : 0;
        fill.style.width = visible.toFixed(2) + '%';
        fill.style.insetInlineStart = (progress * (100 - visible)).toFixed(2) + '%';
      }
    }

    if (prev) prev.addEventListener('click', function () { go(false); });
    if (next) next.addEventListener('click', function () { go(true); });

    // Arrow keys page the track when it has focus. In RTL, ArrowRight is
    // "back" and ArrowLeft is "forward", matching the reading order.
    track.addEventListener('keydown', function (ev) {
      if (ev.key === 'ArrowLeft')  { ev.preventDefault(); go(rtl); }
      if (ev.key === 'ArrowRight') { ev.preventDefault(); go(!rtl); }
      if (ev.key === 'Home') { ev.preventDefault(); track.scrollTo({ left: 0, behavior: 'smooth' }); }
      if (ev.key === 'End')  {
        ev.preventDefault();
        track.scrollTo({ left: (rtl ? -1 : 1) * maxScroll(), behavior: 'smooth' });
      }
    });

    var raf = 0;
    track.addEventListener('scroll', function () {
      if (raf) return;
      raf = requestAnimationFrame(function () { raf = 0; update(); });
    }, { passive: true });

    addEventListener('resize', update, { passive: true });
    // Images settle after layout and change scrollWidth, so re-measure once.
    if (document.readyState === 'complete') update();
    else addEventListener('load', update);
    update();
  });

  /* ---------- category page filtering ------------------------------------
     Operates on the server-rendered cards already in the DOM, so the full
     product list is in the HTML for crawlers whether or not JS runs. */
  var grid = document.getElementById('grid');
  var qEl = document.getElementById('q');
  if (grid && qEl) {
    var cards = [].slice.call(grid.children).map(function (el) {
      var priceEl = el.querySelector('.price');
      var raw = el.getAttribute('data-price');
      return {
        el: el,
        k: norm(el.getAttribute('data-search') || el.textContent),
        brand: el.getAttribute('data-brand') || '',
        axle: el.getAttribute('data-axle') || '',
        price: raw ? parseInt(raw, 10) : null,
        name: el.getAttribute('data-title') || '',
        order: 0
      };
    });
    cards.forEach(function (c, i) { c.order = i; });

    var fb = document.getElementById('fb'), fa = document.getElementById('fa'),
        fs = document.getElementById('fs'), countEl = document.getElementById('count'),
        emptyEl = document.getElementById('empty');

    function apply() {
      var q = expandLetterNames(norm(qEl.value)), b = fb.value, a = fa.value, sort = fs.value, n = 0;
      cards.forEach(function (c) {
        var ok = (!q || c.k.indexOf(q) !== -1) &&
                 (!b || c.brand === b) &&
                 (!a || c.axle === a);
        c.el.hidden = !ok;
        if (ok) n++;
      });
      var vis = cards.filter(function (c) { return !c.el.hidden; });
      if (sort) {
        vis.sort(function (x, y) {
          if (sort === 'name') return x.name.localeCompare(y.name, 'fa');
          if (x.price === null) return 1;
          if (y.price === null) return -1;
          return sort === 'asc' ? x.price - y.price : y.price - x.price;
        });
      } else {
        vis.sort(function (x, y) { return x.order - y.order; });
      }
      vis.forEach(function (c) { grid.appendChild(c.el); });
      countEl.textContent = n ? faDigits(n) + ' کالا' : '';
      emptyEl.hidden = n !== 0;

      var qs = [];
      if (q) qs.push('q=' + encodeURIComponent(qEl.value));
      if (b) qs.push('brand=' + b);
      if (a) qs.push('axle=' + a);
      if (sort) qs.push('sort=' + sort);
      history.replaceState(null, '', qs.length ? '?' + qs.join('&') : location.pathname);
    }

    // hydrate from the URL so the home finder's links land pre-filtered
    var params = new URLSearchParams(location.search);
    if (params.get('q')) qEl.value = params.get('q');
    if (params.get('brand')) fb.value = params.get('brand');
    if (params.get('axle')) fa.value = params.get('axle');
    if (params.get('sort')) fs.value = params.get('sort');

    [qEl, fb, fa, fs].forEach(function (el) {
      el.addEventListener('input', apply);
      el.addEventListener('change', apply);
    });
    apply();
  }
})();
