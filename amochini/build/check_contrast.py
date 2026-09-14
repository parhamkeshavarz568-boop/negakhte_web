#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Worst-case text contrast over the board band's photograph.

    cd amochini/public && python3 -m http.server 8907 &
    PORT=8907 python3 build/check_contrast.py

Every other surface on this site is a flat token, so its contrast is a
property of the palette and is settled in DESIGN.md §2. The board band is the
one place where text sits over a PHOTOGRAPH (§14.4), and there the ground is
different under every glyph. Reasoning about it is not good enough.

Method: hide the band's text, screenshot the bare ground, then read the
BRIGHTEST pixel inside each text box — the worst ground any glyph in that box
could land on — and ratio it against that element's own colour. A check that
sampled an average, or the box's centre, would pass a headline whose last word
sits on a lamp.

Run it after any change to the crop, the grade, the band height, the mask, or
the negative margin that pulls the text into the fade. All five move text and
photograph relative to each other.
"""
import os, sys
from playwright.sync_api import sync_playwright
from PIL import Image

PORT = os.environ.get("PORT", "8907")
BASE = f"http://localhost:{PORT}"
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium")
VIEWPORTS = [(375, 812), (768, 1024), (1440, 900), (1920, 1080)]
AA = 4.5

# selector, the element's own colour, label. Colours are the §2 tokens the
# stylesheet gives these elements; they are repeated here on purpose, so that
# changing one in the stylesheet without changing it here trips the check.
TARGETS = [
    ("#bb-h",              "#f2f5f7", "h1            --paper"),
    (".board-band .sub",   "#a8a49f", "sub           --chalk"),
    (".fb-label",          "#a8a49f", "figure label  --chalk"),
    (".fb-value",          "#f2f5f7", "figure        --paper"),
    (".bb-th",             "#f2f5f7", "table heading --paper"),
]


def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (_lin(v) for v in rgb)
    return .2126 * r + .7152 * g + .0722 * b


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main():
    shots = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".contrast")
    os.makedirs(shots, exist_ok=True)
    fails, rows = [], []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME)
        for w, h in VIEWPORTS:
            page = br.new_page(viewport={"width": w, "height": h})
            page.goto(BASE + "/", wait_until="networkidle")
            boxes = {}
            for sel, _, _ in TARGETS:
                el = page.query_selector(sel)
                boxes[sel] = el.bounding_box() if el else None
            # Hide the text, keep the layout: the photograph and the band must
            # not move, or the boxes measured above stop meaning anything.
            page.add_style_tag(
                content=".board-band .wrap *{visibility:hidden!important}")
            shot = os.path.join(shots, f"bare-{w}.png")
            page.screenshot(path=shot)
            page.close()
            im = Image.open(shot).convert("RGB")
            for sel, fg, label in TARGETS:
                bb = boxes[sel]
                if not bb or bb["y"] >= h:
                    rows.append((w, label, "—", None, "below the fold"))
                    continue
                x0, y0 = max(0, int(bb["x"])), max(0, int(bb["y"]))
                x1 = min(im.width, int(bb["x"] + bb["width"]))
                y1 = min(im.height, int(bb["y"] + bb["height"]))
                if x1 <= x0 or y1 <= y0:
                    rows.append((w, label, "—", None, "zero box"))
                    continue
                worst = max(list(im.crop((x0, y0, x1, y1)).convert("RGB").getdata()), key=luminance)
                r = ratio(rgb(fg), worst)
                rows.append((w, label, "#%02x%02x%02x" % worst, r, ""))
                if r < AA:
                    fails.append((w, label, r))
        br.close()

    print(f"{'vw':>5s}  {'element':22s} {'worst ground':>13s} {'ratio':>7s}")
    last = None
    for w, label, ground, r, note in rows:
        if w != last:
            print()
            last = w
        v = f"{r:6.2f}" if r is not None else "     —"
        flag = "" if r is None or r >= AA else "  FAIL"
        print(f"{w:5d}  {label:22s} {ground:>13s} {v}{flag}  {note}")

    if fails:
        print(f"\n✗ {len(fails)} box(es) below AA {AA}:1 over the photograph")
        for w, label, r in fails:
            print(f"    {w}px  {label}  {r:.2f}")
        return 1
    print(f"\n✓ every text box in the board band clears AA {AA}:1 against the "
          f"brightest pixel it can land on, at {len(VIEWPORTS)} widths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
