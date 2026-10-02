#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The two icons: the house mark — negakhte's gold diamond — on ink.

    python build/make_icons.py

  assets/favicon.svg           browser tab
  assets/apple-touch-icon.png  180x180, "add to home screen" on iPhone (which
                               does not take SVG). Drawn at 4x and downsampled.
"""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
INK, GOLD = "#1F1A15", "#C99846"

SVG = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="{INK}"/>'
       f'<path d="M16 7.5 24.5 16 16 24.5 7.5 16Z" fill="{GOLD}"/></svg>\n')


def touch_icon(size=180, k=4):
    S = size * k
    im = Image.new("RGB", (S, S), INK)
    r = S * 0.25
    c = S / 2
    ImageDraw.Draw(im).polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=GOLD)
    return im.resize((size, size), Image.LANCZOS)


def main():
    with open(os.path.join(ASSETS, "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(SVG)
    touch_icon().save(os.path.join(ASSETS, "apple-touch-icon.png"), optimize=True)
    print("favicon.svg, apple-touch-icon.png")


if __name__ == "__main__":
    main()
