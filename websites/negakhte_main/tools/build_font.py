#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild the subsetted Vazirmatn from the site's own text, and verify it.

    python3 tools/build_font.py            # rebuild + check
    python3 tools/build_font.py --check    # check only, no write

RUN THIS AFTER EDITING ANY PERSIAN TEXT. The font is subset to exactly the
codepoints the site's pages contain, which is the smallest honest set — and also
means a character you add later has no glyph and renders as a tofu box. This
script closes that loop: it re-derives the set from the file and fails if the
shipped font cannot render something the page can display.

Why self-hosted at all: the page used to pull six weights from
fonts.googleapis.com. That is a render-blocking third party, and one that is
unreliable and frequently blocked on Iranian networks — the entire audience
for a Persian-language site. One variable file, same origin, no preconnect.
"""
import glob, json, os, subprocess, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGES = sorted(glob.glob(os.path.join(ROOT, "*.html")))
OUT = os.path.join(ROOT, "assets", "vazirmatn-negakhte.woff2")
# The upstream variable font, vendored in the sibling project.
SRC = os.path.join(ROOT, os.pardir, "amochini", "build", "original", "Vazirmatn[wght].ttf")
LICENCE = os.path.join(ROOT, "assets", "OFL-Vazirmatn.txt")

# The CSS asks for 400-800 and nothing else. Deltas outside that range are
# interpolation no rule can reach.
AXIS = "wght=400:800"
# Shaping and layout characters that must survive even though they are
# invisible, plus everything the page BUILDS at runtime rather than contains
# as a literal (Persian digits, the Persian percent and decimal separators).
KEEP = set("‌‏‎  ") | set("۰۱۲۳۴۵۶۷۸۹0123456789٪٫،؛×÷−–—…«»‌ ")
# Vazirmatn has no glyph for these upstream. They are UI marks, they already
# fell back to a system font before this page was ever subset, and asking for
# them would not conjure them — so they are excluded from the coverage
# assertion rather than silently reported as missing every run.
NO_GLYPH_UPSTREAM = set("←→↔✓")


def needed():
    s = "".join(open(p, encoding="utf-8").read() for p in PAGES)
    use = set(KEEP)
    for c in set(s):
        if c in KEEP:
            continue
        if unicodedata.category(c).startswith("C"):
            continue
        use.add(c)
    return use - NO_GLYPH_UPSTREAM


def build(chars):
    env = dict(os.environ, SOURCE_DATE_EPOCH="1700000000")   # reproducible
    inst = os.path.join(HERE, "_instanced.ttf")
    subprocess.run(["fonttools", "varLib.instancer", SRC, AXIS, "-o", inst],
                   check=True, env=env, capture_output=True)
    uni = ",".join(f"U+{ord(c):04X}" for c in sorted(chars))
    subprocess.run(["pyftsubset", inst, "--flavor=woff2", f"--unicodes={uni}",
                    "--layout-features=*", "--name-IDs=0,1,2,3,4,5,6,13,14",
                    "--drop-tables+=DSIG", f"--output-file={OUT}"],
                   check=True, env=env)
    os.remove(inst)


def check(chars):
    from fontTools.ttLib import TTFont
    f = TTFont(OUT)
    cmap = f.getBestCmap()
    missing = sorted(c for c in chars if ord(c) not in cmap)
    axes = {a.axisTag: (a.minValue, a.maxValue) for a in f["fvar"].axes}
    print(f"  {os.path.getsize(OUT)/1024:.1f} KB   {f['maxp'].numGlyphs} glyphs   "
          f"{len(cmap)} codepoints   wght {axes['wght'][0]:.0f}-{axes['wght'][1]:.0f}")
    if not os.path.isfile(LICENCE):
        print(f"  ✗ {LICENCE} is missing — SIL OFL 1.1 requires the licence to "
              f"ship with the font")
        return 1
    if missing:
        print(f"  ✗ {len(missing)} character(s) the page uses have no glyph:")
        for c in missing:
            print(f"      U+{ord(c):04X}  {c!r}  {unicodedata.name(c, '?')}")
        print("    Re-run without --check to rebuild the subset.")
        return 1
    print(f"  ✓ every one of the {len(chars)} characters the site can display "
          f"has a glyph")
    return 0


def main():
    chars = needed()
    if "--check" not in sys.argv:
        build(chars)
    return check(chars)


if __name__ == "__main__":
    sys.exit(main())
