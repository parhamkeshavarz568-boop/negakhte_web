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
from PIL import Image, ImageFilter
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
    # disk — see _board_band() below.
    "board-band":      [600, 900, 1200],
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
# The board band. The frame this replaced was near-black with two smooth
# amber falloffs — exactly where a low-quality encode bands visibly — so it
# shipped at q=74. This one is a busy still life, and detail is what codecs
# are good at. Swept 34-54 and compared AT THE SIZE IT IS SHOWN (a 1200px
# file in a 1440x245 box, which downscales it and hides artefacts the way the
# real page does): all four are indistinguishable, with no blocking in the
# pad texture or the floor reflections. q=38 is the cheapest with headroom.
Q_BAND = dict(avif=38, webp=52, jpeg=72)

# --------------------------------------------------------------------------
#  board-band — derived at build time from a supplied photograph.
# --------------------------------------------------------------------------
#  The band that opens the board is not a file in original/images/; it is cut
#  and graded here so the recipe is reviewable and the result reproducible.
#
#  THE SOURCE is the shop's own still life: its wall sign, its boxes, and a
#  brake disc, caliper, pad set, filters, battery, belt, plugs and headlight
#  arranged on a wet floor, already lit black-and-amber. It replaced a stock
#  photograph of a Dodge Challenger, which was rejected: it showed a car this
#  shop sells no parts for, and it carried another manufacturer's wordmark.
#
#  1. CROP (0,380)-(1855,760) of the 1855x848 frame, 4.88:1. This window
#     holds the parts and excludes the WALL SIGN above them, which is the
#     point; it is also close to the band's own shape, so `cover` throws away
#     little. The first cut was 4.03:1 and desktop was discarding a third of
#     every row it downloaded. This window holds the
#     parts and excludes the WALL SIGN above them, which is the point: the
#     sign in the photograph reads «شماره عمو چینی» — "Number Uncle Chinese" —
#     and the shop is «عمو چینی». It is the one piece of text in the frame
#     large enough to read at band size, so cropping it out is cheaper and
#     safer than retouching it. The smaller repeats of the same string, on a
#     box and an oil filter, survive the crop but not the downscale: measured
#     at the widest the band is ever shown, they are a few pixels tall.
#  2. SOFTEN the three package wordmarks. The same wrong string is printed
#     small on a box, an oil filter and the battery. They survive the crop
#     because they sit among the parts, so each is replaced by a feathered
#     Gaussian of itself — the packaging keeps its amber-on-black lettering
#     and its logo, and the words stop being words. Small print on a box is
#     what this looks like, which is what packaging looks like anyway. The
#     feather matters: a hard-edged blur leaves a visible rectangle, and at
#     the widest the band is shown that rectangle is bigger than the text was.
#  3. GRADE. The same LUT as before, at much gentler settings. The Challenger
#     frame was a bright studio shot that needed γ=2.2 to become a dark band.
#     This one arrives dark and in the site's own two colours, so heavy
#     grading only muddies it: γ=1.25 keeps the amber highlights where the
#     photographer put them, and the mix does the rest.
BOARD_RGB = (0x1a, 0x15, 0x0f)     # --board, DESIGN.md §2
BAND_GAMMA = 1.25
BAND_MIX = 0.30                    # see DESIGN.md §14.4 for the sweep
BAND_CROP = (0, 380, 1855, 760)
# Source-frame coordinates, so re-cropping the band cannot move them off the
# text. Each is a printed «شماره عمو چینی» — the shop is «عمو چینی».
BAND_WORDMARKS = ((196, 584, 364, 632),     # the yellow box, front left
                  (658, 636, 778, 672),     # the oil filter, centre
                  (1126, 592, 1232, 620))   # the battery label


def _soften(im, box, radius=7, feather=6):
    """Blur `box` into oblivion and blend the result back with soft edges."""
    from PIL import ImageDraw
    x0, y0, x1, y1 = box
    pad = feather * 2
    outer = (max(0, x0 - pad), max(0, y0 - pad),
             min(im.width, x1 + pad), min(im.height, y1 + pad))
    patch = im.crop(outer).filter(ImageFilter.GaussianBlur(radius))
    mask = Image.new("L", (outer[2] - outer[0], outer[3] - outer[1]), 0)
    ImageDraw.Draw(mask).rectangle(
        (x0 - outer[0], y0 - outer[1], x1 - outer[0], y1 - outer[1]), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    im.paste(patch, outer[:2], mask)
    return im


def _board_band():
    im = Image.open(os.path.join(SRC, "supplied", "hero-parts.png")).convert("RGB")
    assert im.size == (1855, 848), f"source frame changed: {im.size}"
    for box in BAND_WORDMARKS:
        _soften(im, box)
    im = im.crop(BAND_CROP)
    lut = []
    for floor in BOARD_RGB:
        lut += [min(255, int(floor + (1 - BAND_MIX)
                             * (v / 255.0) ** BAND_GAMMA * (255 - floor) + .5))
                for v in range(256)]
    return im.point(lut)


PREP = {"board-band": _board_band}


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
                 else Q_BAND if name == "board-band"
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
