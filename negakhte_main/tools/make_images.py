#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The homepage's photographs: masters -> the files the page ships.

    python tools/make_images.py

images/source/*.jpg   the masters (see images/source/MANIFEST.json)
assets/img/           what home.html loads: <name>-<width>.avif / .webp at 640,
                      1024 and 1536 px wide (never wider than the master), and
                      og-home.jpg, the 1200x630 card shown when the homepage is
                      shared on Telegram or WhatsApp.

The masters are generated images, made by the owner from written prompts, of
objects, light and nature only: no person appears in any of them, by rule.
Incremental: a rendition is rebuilt only when its master is newer.
"""
import json, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "images", "source")
OUT = os.path.join(ROOT, "assets", "img")
WIDTHS = (640, 1024, 1536)
AVIF = dict(quality=55, speed=6)
WEBP = dict(quality=80, method=6)


def main():
    force = "--all" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    sizes, made = {}, 0
    for f in sorted(os.listdir(SRC)):
        if not f.endswith(".jpg"):
            continue
        name, src = f[:-4], os.path.join(SRC, f)
        im = Image.open(src).convert("RGB")
        W, H = im.size
        ws = sorted({min(w, W) for w in WIDTHS})
        for w in ws:
            h = round(H * w / W)
            for ext, kw in (("avif", AVIF), ("webp", WEBP)):
                out = os.path.join(OUT, f"{name}-{w}.{ext}")
                if force or not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
                    im.resize((w, h), Image.LANCZOS).save(out, ext.upper(), **kw)
                    made += 1
        sizes[name] = {"size": [W, H], "widths": ws}
    # the share card: the ripples, cropped to 1200x630 around the drop
    hero = Image.open(os.path.join(SRC, "ripples-wide.jpg")).convert("RGB")
    W, H = hero.size
    ch = round(W * 630 / 1200)
    top = (H - ch) // 2
    hero.crop((0, top, W, top + ch)).resize((1200, 630), Image.LANCZOS).save(
        os.path.join(OUT, "og-home.jpg"), "JPEG", quality=82, optimize=True, progressive=True)
    with open(os.path.join(OUT, "sizes.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sizes, fh, indent=1)
    total = sum(os.path.getsize(os.path.join(OUT, x)) for x in os.listdir(OUT))
    print(f"{len(sizes)} images, {made} files written, assets/img = {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
