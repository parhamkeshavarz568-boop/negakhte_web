#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout and Core Web Vitals check, in a real browser.

    python3 -m http.server 8907 --directory public &
    PORT=8907 python3 build/check_layout.py

Checks, per page and per viewport:

  1. SCROLL-HEIGHT STABILITY. The document height must not change as you
     scroll through it. This is the check that caught `content-visibility:
     auto` producing 765px of phantom height — the page reported 12840px on
     load and collapsed to 12075px once scrolled, letting the user scroll
     into space that stopped existing. Re-run this before reintroducing any
     content-visibility or contain-intrinsic-size rule.
  2. NO HORIZONTAL OVERFLOW at any viewport.
  3. NO STUCK REVEALS. Scroll-driven entry animations must never leave
     on-screen content invisible — if `animation-fill-mode` or the range is
     wrong, above-fold cards stay at opacity 0 and the page looks empty.
  4. CLS, LCP and long tasks from the real PerformanceObserver entries.
  5. FOOTER IS LAST. Nothing may sit below the footer holding the scroll
     area open over emptiness.
"""
import os, sys
from playwright.sync_api import sync_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PORT = os.environ.get("PORT", "8907")
BASE = f"http://localhost:{PORT}"
PAGES = ["/", "/brake-discs/", "/brake-pads/", "/brands/mvm/",
         "/brake-discs/mvm-33x-rear-tra-x/", "/contact/", "/about/"]
VIEWPORTS = [("mobile", 390, 844), ("tablet", 768, 1024), ("desktop", 1440, 900)]

# Thresholds: Google's "good" bar for CLS, and a deliberately tight local
# LCP budget — a static file off localhost has no excuse.
CLS_MAX = 0.10
LCP_MAX_MS = 1500

VITALS = """
window.__v = {cls:0, lcp:0, long:0};
new PerformanceObserver(l => { for (const e of l.getEntries())
  if (!e.hadRecentInput) window.__v.cls += e.value; }).observe({type:'layout-shift', buffered:true});
new PerformanceObserver(l => { const es=l.getEntries();
  window.__v.lcp = es[es.length-1].startTime; }).observe({type:'largest-contentful-paint', buffered:true});
new PerformanceObserver(l => { window.__v.long += l.getEntries().length; })
  .observe({type:'longtask', buffered:true});
"""


def main():
    fails, rows = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for vname, w, h in VIEWPORTS:
            ctx = b.new_context(viewport={"width": w, "height": h},
                                device_scale_factor=2)
            ctx.add_init_script(VITALS)
            pg = ctx.new_page()
            for url in PAGES:
                pg.goto(BASE + url, wait_until="networkidle")
                pg.wait_for_timeout(600)

                h0 = pg.evaluate("()=>document.documentElement.scrollHeight")
                overflow = pg.evaluate(
                    "()=>document.documentElement.scrollWidth > "
                    "document.documentElement.clientWidth + 1")
                stuck = pg.evaluate("""()=>{
                  const els=[...document.querySelectorAll(
                    '.card,.cat,.features li,.brandgrid a')];
                  return els.filter(e=>{
                    const r=e.getBoundingClientRect();
                    if (r.top >= innerHeight*0.6 || r.bottom <= 0) return false;
                    return parseFloat(getComputedStyle(e).opacity) < 0.5;
                  }).length;
                }""")
                pg.evaluate("()=>window.scrollTo(0,document.documentElement.scrollHeight)")
                pg.wait_for_timeout(800)
                h1 = pg.evaluate("()=>document.documentElement.scrollHeight")
                gap = pg.evaluate("""()=>{
                  const f=document.querySelector('footer');
                  if(!f) return 0;
                  return Math.round(document.documentElement.scrollHeight -
                                    (f.getBoundingClientRect().bottom + scrollY));
                }""")
                pg.evaluate("()=>window.scrollTo(0,0)")
                pg.wait_for_timeout(300)
                h2 = pg.evaluate("()=>document.documentElement.scrollHeight")
                v = pg.evaluate("()=>window.__v")

                drift = max(abs(h1 - h0), abs(h2 - h0))
                if drift > 2:
                    fails.append(f"{vname} {url}: scroll height drifts {drift}px "
                                 f"({h0} -> {h1} -> {h2})")
                if overflow:
                    fails.append(f"{vname} {url}: horizontal overflow")
                if stuck:
                    fails.append(f"{vname} {url}: {stuck} on-screen element(s) "
                                 f"stuck below 0.5 opacity — reveal animation")
                if gap > 2:
                    fails.append(f"{vname} {url}: {gap}px of page below the footer")
                if v["cls"] > CLS_MAX:
                    fails.append(f"{vname} {url}: CLS {v['cls']:.3f} > {CLS_MAX}")
                if v["lcp"] > LCP_MAX_MS:
                    fails.append(f"{vname} {url}: LCP {v['lcp']:.0f}ms > {LCP_MAX_MS}ms")
                rows.append((vname, url, h0, drift, v["cls"], v["lcp"], v["long"]))
            ctx.close()
        b.close()

    print(f"{'viewport':9s} {'page':34s} {'height':>7s} {'drift':>6s} "
          f"{'CLS':>6s} {'LCP':>8s} {'long':>5s}")
    for vname, url, h0, drift, cls, lcp, lng in rows:
        print(f"{vname:9s} {url:34s} {h0:7d} {drift:6d} {cls:6.3f} "
              f"{lcp:7.0f}ms {lng:5d}")
    if fails:
        print(f"\n{len(fails)} FAILURE(S):")
        for f in fails:
            print("   ✗", f)
        return 1
    print(f"\n✓ {len(rows)} page/viewport combinations: heights stable, no "
          f"overflow, no stuck reveals, CLS < {CLS_MAX}, LCP < {LCP_MAX_MS}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
