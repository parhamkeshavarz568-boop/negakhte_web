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
# 150 KB: mobile pages all land 75-110 KB; the desktop home page is heaviest
# at ~141 KB because it serves the 1500px hero, which is the largest rendition
# the source image can provide. Raise this only with a reason.
BUDGET_KB = 150


def main():
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "public")
    worst = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for vname, w, h in VIEWPORTS:
            print(f"\n===== {vname} {w}x{h} @ DPR 2 =====")
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
                worst = max(worst, gztotal / 1024)
                flag = "" if gztotal / 1024 <= BUDGET_KB else "  <-- OVER BUDGET"
                print(f"  {pname:9s} {len(rows):2d} req   "
                      f"over-the-wire {gztotal/1024:6.1f} KB{flag}")
                for rel, g in sorted(rows, key=lambda r: -r[1])[:4]:
                    print(f"                {g/1024:6.1f} KB  {rel}")
                ctx.close()
        b.close()
    print(f"\nheaviest page: {worst:.1f} KB   budget: {BUDGET_KB} KB")
    return 0 if worst <= BUDGET_KB else 1


if __name__ == "__main__":
    sys.exit(main())
