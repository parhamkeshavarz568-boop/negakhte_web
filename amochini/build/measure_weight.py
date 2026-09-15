#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure real first-load transfer weight in Chromium, per page and viewport.

The point is not the byte count alone — it is WHICH renditions a real browser
actually chooses from the AVIF/WebP/JPEG negotiation and the srcset widths.
Serves from a plain local server, so sizes come from the files on disk; the
over-the-wire column gzips the textual ones the way the host will.
"""
import os, gzip, sys
from playwright.sync_api import sync_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PORT = os.environ.get("PORT", "8901")
BASE = f"http://localhost:{PORT}"
PAGES = [("home", "/"), ("category", "/brake-pads/"),
         ("product", "/brake-pads/mvm-315-front/"), ("brand", "/brands/mvm/")]
VIEWPORTS = [("mobile", 390, 844), ("desktop", 1440, 900)]
TEXTUAL = (".html", ".css", ".js", ".json", ".xml", ".svg", "/")
# One budget per viewport, because the two are not the same constraint.
#
#   mobile  150 KB — THE budget. It exists for an Iranian mobile connection,
#           and that is the number worth defending. Every mobile page lands
#           75-139 KB; the home page, the only one carrying a photograph, is
#           the ceiling at ~139.
#
#   desktop 170 KB — the same page measured at DPR 2, where a 1440px band asks
#           for a 2880px image and gets the source's full 1855px rendition,
#           26 KB. Held at one shared 150 the only ways to fit were to ship a
#           visibly soft hero (tried; the owner caught it in one look) or to
#           cut the photograph. Desktop DPR-2 users are on fixed lines. The
#           number is here so that overrunning it is still a decision and not
#           a drift — raise it only with a reason, in writing.
#
# What was NOT done to make this fit, and should be tried before it is raised
# again: 73.9 KB of the base is two webfonts. Vazirmatn is already subset and
# axis-limited; Lalezar is 19.6 KB for the display face. That is the next real
# saving on every page, not just this one.
BUDGET_KB = {"mobile": 150, "desktop": 170}


def main():
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "public")
    worst = float("-inf")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for vname, w, h in VIEWPORTS:
            budget = BUDGET_KB[vname]
            print(f"\n===== {vname} {w}x{h} @ DPR 2   budget {budget} KB =====")
            for pname, url in PAGES:
                ctx = b.new_context(viewport={"width": w, "height": h},
                                    device_scale_factor=2)
                pg = ctx.new_page()
                seen = []
                pg.on("response", lambda r: seen.append(r.url))
                pg.goto(BASE + url, wait_until="load")
                pg.wait_for_timeout(800)
                total = gztotal = 0
                rows = []
                for u in seen:
                    rel = u.replace(BASE, "")
                    fp = os.path.join(root, rel.lstrip("/"))
                    if rel.endswith("/"):
                        fp = os.path.join(fp, "index.html")
                    if not os.path.isfile(fp):
                        continue
                    n = os.path.getsize(fp)
                    g = (len(gzip.compress(open(fp, "rb").read(), 9))
                         if rel.endswith(TEXTUAL) else n)
                    total += n
                    gztotal += g
                    rows.append((rel, g))
                over = gztotal / 1024 - budget
                worst = max(worst, over)
                flag = "" if over <= 0 else f"  <-- {over:.1f} KB OVER BUDGET"
                print(f"  {pname:9s} {len(rows):2d} req   "
                      f"over-the-wire {gztotal/1024:6.1f} KB{flag}")
                for rel, g in sorted(rows, key=lambda r: -r[1])[:4]:
                    print(f"                {g/1024:6.1f} KB  {rel}")
                ctx.close()
        b.close()
    if worst <= 0:
        print(f"\n✓ every page is inside its viewport's budget "
              f"(mobile {BUDGET_KB['mobile']} KB, desktop {BUDGET_KB['desktop']} KB); "
              f"tightest margin {-worst:.1f} KB")
        return 0
    print(f"\n✗ worst page is {worst:.1f} KB over its budget")
    return 1


if __name__ == "__main__":
    sys.exit(main())
