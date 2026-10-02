#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The two icons, drawn from the same arched window as the logo mark.

    python build/make_icons.py

  assets/favicon.svg           browser tab — gold window on wine
  assets/apple-touch-icon.png  180x180, "add to home screen" on iPhone (which
                               does not take SVG). Drawn at 4x and downsampled
                               so the arch is smooth.
"""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
WINE, GOLD, PANE = "#3F1610", "#C99846", "#6A2717"

# the mark's arch, in its own 24x30 units: two cubic curves meeting at the top
ARCH = [((2, 12.5), (2, 6.6), (6.5, 2.3), (12, 1)), ((12, 1), (17.5, 2.3), (22, 6.9), (22, 12.5))]

SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="{WINE}"/><g transform="translate(4 1)"><path d="M2 29V12.5C2 6.6 6.5 2.3 12 1c5.5 1.3 10 5.6 10 11.5V29Z" fill="{PANE}" stroke="{GOLD}" stroke-width="2"/><path d="M12 3.5v25.5M2.8 16h18.4" stroke="{GOLD}" stroke-width="1.6"/></g></svg>
"""


def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def touch_icon(size=180, k=4):
    S = size * k
    im = Image.new("RGB", (S, S), WINE)
    d = ImageDraw.Draw(im)
    scale = S * 0.62 / 30                       # the arch is 30 units tall
    ox, oy = (S - 24 * scale) / 2, S * 0.19
    pt = lambda x, y: (ox + x * scale, oy + y * scale)
    outline = [pt(2, 29)] + [pt(*q) for seg in ARCH for q in bezier(*seg)] + [pt(22, 29)]
    d.polygon(outline, fill=PANE)
    d.line(outline + [outline[0]], fill=GOLD, width=int(2.0 * scale), joint="curve")
    d.line([pt(12, 3.2), pt(12, 29)], fill=GOLD, width=int(1.6 * scale))
    d.line([pt(2.8, 16), pt(21.2, 16)], fill=GOLD, width=int(1.6 * scale))
    return im.resize((size, size), Image.LANCZOS)


def main():
    with open(os.path.join(ASSETS, "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(SVG)
    touch_icon().save(os.path.join(ASSETS, "apple-touch-icon.png"), optimize=True)
    print("favicon.svg, apple-touch-icon.png")


if __name__ == "__main__":
    main()
