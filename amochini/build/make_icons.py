#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cut the brand mark out of the supplied poster, then build the logo renditions
and the whole favicon / app-icon set from it.

The mark is the real عمو چینی logo: an amber gear ring around a white curly
head with a moustache. It arrives inside a promotional poster
(original/images/supplied/logo-poster.png, 1086x1448), so the crop and the
colour key live here rather than in a hand-edited PNG — that way the whole set
is reproducible from the file the owner actually sent.

Measured, not guessed. Scanning the poster's top 44% for pixels above
luminance 110, ignoring the paint splatters at the outer edges, puts the mark
at x 214..936, y 80..636; the row profile shows the gear-and-hair mass ending
at y~500, a gap, then the moustache at y 536..608, and the «شماره عمو چینی»
wordmark starting below y~620. Hence the crop below.

The key is a two-colour classification rather than a luminance ramp: the gear
carries a 3D drop shadow in the poster, and a ramp left a muddy brown fringe
around it. Classifying in HSV and repainting flat --amber and --paper gives a
clean mark, drops the shadow, and matches a design system that has no shadows
in it (DESIGN.md §7).
"""
import colorsys, math, os, sys
from PIL import Image, ImageDraw

try:
    import pillow_avif  # noqa: F401
    HAVE_AVIF = True
except ImportError:
    HAVE_AVIF = False

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "public")
IMG = os.path.join(OUT, "assets", "img")
POSTER = os.path.join(HERE, "original", "images", "supplied", "logo-poster.png")

CROP = (208, 72, 942, 620)     # see the module docstring
AMBER = (247, 174, 12)         # --amber
PAPER = (242, 245, 247)        # --paper
BOARD = (26, 21, 15)           # --board

# The masthead mark renders at 44px tall on a phone and 52px on desktop, so
# 1x/2x/3x of the widest case. The mark is flat two-colour, so each rendition
# is a couple of kilobytes.
LOGO_WIDTHS = [70, 140, 210]


def mark():
    """The logo, keyed to RGBA and tight-cropped to its ink."""
    src = Image.open(POSTER).convert("RGB")
    crop = src.crop(CROP)
    w, h = crop.size
    px = crop.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            hh, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            deg = hh * 360
            if v > 0.32 and s > 0.45 and 33 <= deg <= 62:
                op[x, y] = AMBER + (255,)        # the gear
            elif v > 0.55 and s < 0.22:
                op[x, y] = PAPER + (255,)        # hair and moustache
    return out.crop(out.getbbox())


def on_ground(m, size, radius_ratio=0.16, pad=0.10):
    """The mark centred on a --board tile, for the app icons, which cannot be
    transparent (Android and iOS composite them onto their own surfaces)."""
    S = size * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle(
        [0, 0, S - 1, S - 1], radius=int(S * radius_ratio), fill=BOARD)
    inner = int(S * (1 - 2 * pad))
    r = m.copy()
    r.thumbnail((inner, inner), Image.LANCZOS)
    im.paste(r, ((S - r.width) // 2, (S - r.height) // 2), r)
    return im.resize((size, size), Image.LANCZOS)


def main():
    if not os.path.isfile(POSTER):
        print(f"logo source not found: {POSTER}")
        return 1
    os.makedirs(IMG, exist_ok=True)
    m = mark()
    print(f"  mark keyed from the poster: {m.width}x{m.height}")

    # ---- the masthead logo ----
    # Quantised to six colours (two flat inks plus the anti-aliasing steps
    # between them and transparency) and shipped as LOSSLESS WebP with a
    # palettised PNG fallback. Measured at 140px: 1.5 KB lossless WebP and
    # 2.3 KB PNG8, against 7.9 KB lossy WebP and 5.6 KB AVIF from the full
    # RGBA source. AVIF is deliberately NOT shipped for the mark — its
    # transform coding is the wrong tool for hard-edged flat art and it came
    # out twice the size of the WebP. The logo is on all 155 pages, so this
    # is ~4 KB a page.
    for w in LOGO_WIDTHS:
        r = m.copy()
        r.thumbnail((w, w * 4), Image.LANCZOS)
        q = r.quantize(colors=6, method=Image.FASTOCTREE)
        base = os.path.join(IMG, f"logo-{w}")
        q.save(base + ".png", optimize=True)
        q.convert("RGBA").save(base + ".webp", lossless=True, method=6)
        for stale in (base + ".avif", base + ".jpg"):
            if os.path.exists(stale):
                os.remove(stale)
        made = " ".join(
            f"{ext}:{os.path.getsize(base + '.' + ext) / 1024:.1f}K"
            for ext in ("png", "webp"))
        print(f"  logo-{w:<3d} {r.width}x{r.height}  {made}")

    # ---- app icons ----
    for size, name in [(180, "apple-touch-icon.png"),
                       (192, "icon-192.png"),
                       (512, "icon-512.png")]:
        on_ground(m, size).save(os.path.join(OUT, name), optimize=True)
    # Maskable must sit inside Android's circular safe zone, so the tile is a
    # full circle and the mark is inset further.
    on_ground(m, 512, radius_ratio=0.5, pad=0.20).save(
        os.path.join(OUT, "icon-maskable-512.png"), optimize=True)
    on_ground(m, 32).save(os.path.join(OUT, "favicon-32.png"), optimize=True)
    on_ground(m, 48).save(os.path.join(OUT, "favicon.ico"), format="ICO",
                          sizes=[(16, 16), (32, 32), (48, 48)])
    # No favicon.svg any more: the mark is a raster photograph-derived shape
    # and there is no faithful vector of it. An SVG wrapping a base64 PNG
    # would be a lie about the format and bigger than the PNG.
    stale = os.path.join(OUT, "favicon.svg")
    if os.path.exists(stale):
        os.remove(stale)
    for f in ["favicon.ico", "favicon-32.png", "apple-touch-icon.png",
              "icon-192.png", "icon-512.png", "icon-maskable-512.png"]:
        p = os.path.join(OUT, f)
        print(f"  {f:26s} {os.path.getsize(p) / 1024:6.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
