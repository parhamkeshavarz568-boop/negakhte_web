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
    # The band that opens the board (DESIGN.md §14.4). Derived, not a file on
    # disk — see _brake_lights() below. 1200 is the honest ceiling; the source
    # is 1200 wide and upscaling a photograph is fake detail.
    "brake-lights":    [600, 900, 1200],
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
# The brake-light band. The frame it replaced was near-black with two smooth
# amber falloffs, which is exactly where a low-quality encode bands visibly,
# so it was shipped at q=74. This frame is the opposite: smoke fills it edge
# to edge, and noise is what codecs are good at. Swept 44-74 at 1200px and
# compared at 1:1 and at 2x — q=50 is indistinguishable from q=74 with no
# banding anywhere in the dark falloff, at 9.4 KB instead of 18.3 KB. That
# difference is the whole reason the desktop home page fits its budget
# (156.5 KB at q=74; the budget is 150).
Q_LIGHTS = dict(avif=50, webp=64, jpeg=74)

# --------------------------------------------------------------------------
#  brake-lights — derived at build time from a supplied photograph.
# --------------------------------------------------------------------------
#  The band that opens the board is not a file in original/images/; it is cut
#  and graded here so the recipe is reviewable and the result reproducible.
#  Three operations, in order, each for a stated reason:
#
#  1. CROP (0,380)-(1200,640) of the 1200x675 supplied frame. This window
#     holds the tail-light bars at roughly a third down and the lit smoke
#     below them, and excludes the roofline — what is wanted is the light
#     signature, not a recognisable car.
#  2. RETOUCH. The frame carries the manufacturer's wordmark twice: once
#     illuminated between the light bars, once on the plate below. This site
#     sells Chinese-car brake parts; another carmaker's wordmark across the
#     masthead of the price board is somebody else's brand on ours. Both are
#     erased with a local blur of their own surroundings, which on a smooth
#     dark gradient leaves nothing to see.
#  3. GRADE. A per-channel gamma curve with the board colour as its black
#     floor. Gamma crushes the smoke (a mid grey at 150 lands near 90) while
#     leaving the lamps alone (240 stays above 220) — a linear multiply would
#     have taken the lamps down with the smoke and killed the only light in
#     the frame. The floor means the darkest pixel IS --board, so the
#     photograph's edges dissolve into the band instead of sitting on it as a
#     slightly-different black.
BOARD_RGB = (0x1a, 0x15, 0x0f)     # --board, DESIGN.md §2
LIGHTS_GAMMA = 2.2


def _brake_lights():
    from PIL import ImageFilter
    im = Image.open(os.path.join(SRC, "supplied",
                                 "challenger-rear-red-smoke.jpg")).convert("RGB")
    assert im.size == (1200, 675), f"source frame changed: {im.size}"
    # Wordmark boxes are given in SOURCE-frame coordinates and shifted by the
    # crop, so re-cropping the band cannot silently move the retouch off them.
    TOP = 380
    im = im.crop((0, TOP, 1200, 640))
    for (x0, y0, x1, y1), radius in ((( 548, 512,  648, 556), 9),    # the plate
                                     (( 562, 450,  646, 482), 7)):   # lit wordmark
        box = (x0, y0 - TOP, x1, y1 - TOP)
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(radius)), box)
    lut = []
    for floor in BOARD_RGB:
        lut += [min(255, int(floor + (v / 255.0) ** LIGHTS_GAMMA * (255 - floor) + .5))
                for v in range(256)]
    return im.point(lut)


PREP = {"brake-lights": _brake_lights}


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
        if name in PREP:
            im = PREP[name]()
        else:
            im = Image.open(os.path.join(SRC, f"{name}.jpg")).convert("RGB")
        ow, oh = im.size
        for w in widths:
            w = min(w, ow)
            h = max(1, round(oh * w / ow))
            r = im.resize((w, h), Image.LANCZOS)
            q = (Q_HERO if name.startswith("hero")
                 else Q_LIGHTS if name == "brake-lights"
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
