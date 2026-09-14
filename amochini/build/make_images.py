#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the image set from the originals decoded out of the draft.

Sizes are not guessed — they come from measuring the real rendered boxes in
headless Chromium at 390/768/1440 CSS px (see docs/MEASUREMENTS.md):

    hero          390x541, 768x589, 1440x597   -> full-bleed, 640/1024/1500
    category thumb    160x160 (image-forward)   -> 160 and 320 (2x)
    product card  187 / 245 / 283              -> 400 and 600
    product photo 318 / 380 / 380              -> 400 and 700

The category thumbnails were being shipped at 400px into a 108px box — a 3.4x
pixel-count overspend on every home-page load.

Formats: AVIF first, WebP second, JPEG last. WebP is the layer doing the real
work for the older Android tail common in Iran; AVIF is the byte win for
everything current.
"""
import os, re, sys
from PIL import Image
try:
    import pillow_avif  # noqa: F401  registers the AVIF plugin
    HAVE_AVIF = True
except ImportError:
    HAVE_AVIF = False

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "original", "images")
OUT = os.path.join(os.path.dirname(HERE), "public", "assets", "img")

PLAN = {
    "hero-bg":         [640, 1024, 1500],
    # Category cards are image-forward in the redesign: a 160px CSS square,
    # so 160 (1x) and 320 (2x). The sources are 400x400, so 320 is the
    # largest honest rendition — asking for more would just upscale.
    # 160/320 for the image-forward category card; 400 because the same files
    # are reused as product-card images, which render up to 283 CSS px (566 at
    # DPR 2 — 400 is the largest the 400x400 sources honestly support).
    # 80 is the board's row thumbnail at DPR 2 (a 40px box). Without it the
    # board reached for a 160px file per row, and the disc photos reached for
    # a 400px one — 11.7 KB to fill 40 pixels.
    "cat-brake-pads":  [80, 160, 320, 400],
    "cat-brake-discs": [80, 160, 320, 400],
    "cat-headlight":   [160, 320, 400],
    # A tight, darkened crop of the plain-disc studio shot. There is no real
    # کاسه چرخ photo, and the untouched white-cloth original sat beside two
    # dark studio photos in the same three-card row, which read as a
    # mismatched set. Still a placeholder — see docs/PLACEHOLDERS.md.
    "cat-brake-drums": [80, 160, 320, 400],
    # The headlight band that closes the board (DESIGN.md §14.4). A measured
    # 1200x200 crop of the supplied amber-headlights-on-black photograph: the
    # bright band sits at y 606-689 of the 900px original, so this window
    # centres it with a little more black below. 1200 is the honest ceiling —
    # the source is 1200 wide and upscaling a photograph is fake detail. It is
    # almost entirely black, so it compresses to a few KB.
    "lights-band":     [600, 900, 1200],
    "disc-drilled":    [80, 160, 400, 600, 700],
    "disc-slotted":    [80, 160, 400, 600, 700],
    "disc-plain":      [80, 160, 400, 600, 700],
}
Q = dict(avif=54, webp=79, jpeg=78)
# The hero is overlaid by a linear-gradient scrim running rgba(0,0,0,.82) to
# rgba(0,0,0,.15). At that opacity its detail is not visible, so it carries a
# much lower quality than the product photos: 30 KB instead of 57 KB at 1500px
# for a difference nobody can see through the scrim.
Q_HERO = dict(avif=38, webp=62, jpeg=68)
# The headlight band is the opposite case: a near-black frame with two smooth
# amber gradients, which is exactly where a low-quality AVIF bands visibly —
# the dark falloff broke into steps at q=54 and read as a cheap image. It is
# 200px tall and mostly black, so near-lossless still lands in single-digit
# kilobytes. Worth every byte; this is the one photograph on the site.
Q_LIGHTS = dict(avif=74, webp=90, jpeg=92)


def main():
    os.makedirs(OUT, exist_ok=True)
    # Only sweep the renditions THIS script owns. It used to clear the whole
    # directory, which silently deleted the logo and the social card that
    # make_icons.py writes into the same folder — whenever the two ran in the
    # wrong order the masthead shipped a broken image. A build step must not
    # delete files it did not create.
    mine = set(PLAN)
    for f in os.listdir(OUT):
        m = re.match(r"(.+)-\d+\.(avif|webp|jpg|png)$", f)
        if m and m.group(1) in mine:
            os.remove(os.path.join(OUT, f))
    rows, tot = [], 0
    for name, widths in PLAN.items():
        src = os.path.join(SRC, f"{name}.jpg")
        im = Image.open(src).convert("RGB")
        ow, oh = im.size
        for w in widths:
            w = min(w, ow)
            h = max(1, round(oh * w / ow))
            r = im.resize((w, h), Image.LANCZOS)
            q = (Q_HERO if name.startswith("hero")
                 else Q_LIGHTS if name == "lights-band"
                 else Q)
            made = {}
            if HAVE_AVIF:
                p = f"{OUT}/{name}-{w}.avif"
                r.save(p, "AVIF", quality=q["avif"])
                made["avif"] = os.path.getsize(p)
            p = f"{OUT}/{name}-{w}.webp"
            r.save(p, "WEBP", quality=q["webp"], method=6)
            made["webp"] = os.path.getsize(p)
            p = f"{OUT}/{name}-{w}.jpg"
            r.save(p, "JPEG", quality=q["jpeg"], optimize=True, progressive=True)
            made["jpeg"] = os.path.getsize(p)
            tot += sum(made.values())
            rows.append((name, w, h, made))
    print(f"{'image':18s} {'w':>5s} {'h':>5s} {'avif':>8s} {'webp':>8s} {'jpeg':>8s}")
    for n, w, h, m in rows:
        print(f"{n:18s} {w:5d} {h:5d} "
              f"{m.get('avif',0)/1024:7.1f}K {m['webp']/1024:7.1f}K {m['jpeg']/1024:7.1f}K")
    print(f"\n{len(rows)} renditions, {tot/1024:.0f} KB on disk"
          f"{'' if HAVE_AVIF else '  (AVIF SKIPPED — pillow-avif-plugin not installed)'}")
    if HAVE_AVIF:
        a = sum(m.get("avif", 0) for *_x, m in rows)
        j = sum(m["jpeg"] for *_x, m in rows)
        print(f"AVIF is {100-a/j*100:.0f}% smaller than JPEG across the set")


if __name__ == "__main__":
    main()
