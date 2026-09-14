#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the favicon and app-icon set.

The mark is a brake disc — the thing this shop actually sells — in the brand
yellow on near-black. Drawn at 4x and downsampled so the small sizes stay
crisp without hinting.
"""
import math, os, shutil, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "public")
SRC_SVG = os.path.join(HERE, "original", "favicon.svg")


def disc(size, radius_ratio=0.16):
    S = size * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, S - 1, S - 1],
                        radius=int(S * radius_ratio), fill="#1f1f1f")
    c = S / 2
    R = S * 0.328
    d.ellipse([c - R, c - R, c + R, c + R], outline="#fbb316",
              width=max(2, int(S * 0.0625)))
    r2 = S * 0.125
    d.ellipse([c - r2, c - r2, c + r2, c + r2], outline="#fbb316",
              width=max(2, int(S * 0.047)))
    hr, hs = S * 0.234, S * 0.036
    for k in range(8):
        a = math.radians(k * 45)
        hx, hy = c + hr * math.cos(a), c + hr * math.sin(a)
        d.ellipse([hx - hs, hy - hs, hx + hs, hy + hs], fill="#fbb316")
    return im.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for size, name in [(180, "apple-touch-icon.png"),
                       (192, "icon-192.png"),
                       (512, "icon-512.png")]:
        disc(size).save(os.path.join(OUT, name))
    # Maskable needs the mark inside Android's circular safe zone, so the
    # rounded rect becomes a full circle rather than being clipped square.
    disc(512, radius_ratio=0.5).save(os.path.join(OUT, "icon-maskable-512.png"))
    disc(48).save(os.path.join(OUT, "favicon.ico"), format="ICO",
                  sizes=[(16, 16), (32, 32), (48, 48)])
    shutil.copy(SRC_SVG, os.path.join(OUT, "favicon.svg"))
    for f in ["favicon.svg", "favicon.ico", "apple-touch-icon.png",
              "icon-192.png", "icon-512.png", "icon-maskable-512.png"]:
        p = os.path.join(OUT, f)
        print(f"  {f:26s} {os.path.getsize(p)/1024:6.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
