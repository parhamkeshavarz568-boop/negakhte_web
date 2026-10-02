#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the self-hosted Vazirmatn subset.

    python3 build/make_font.py            # uses a vendored source if present
    python3 build/make_font.py <path.ttf> # or point at Vazirmatn[wght].ttf

Why self-hosted at all: the draft loaded this font from cdn.jsdelivr.net,
which is Cloudflare anycast. Iran does SNI-based blocking of Cloudflare edge
IPs, and a stalled font request does not fail fast — it holds up first paint.
cdnjs and unpkg are the same network, so they are not fallbacks.

Why ONE variable file: the upstream v33.003 stylesheet declares nine static
faces and the design genuinely uses 400/450/500/550/600/700 — weights static
files cannot express without silently snapping. One variable file covers
100-900 in a single request.

Why an explicit codepoint list rather than the whole Arabic block: only 49 of
256 Arabic-block codepoints are ever rendered, but the search box means a user
can TYPE any Persian letter — including the Arabic look-alikes ي ك ة ى that a
non-Persian keyboard produces. So the set is the Persian alphabet plus those
look-alikes plus ASCII (the product codes are AMO-###, TRA-X, CS35, KMC X5),
not "whatever the copy happens to contain today".

Vazirmatn v33.003 is the final release — its author, Saber Rastikerdar, died in
November 2023. Vendor it and pin it; there will be no upstream update.
SIL OFL 1.1 requires the licence to travel with the font, so OFL.txt ships
alongside and the copyright name records are preserved (--name-IDs).
"""
import os, shutil, subprocess, sys

# Reproducible output. fontTools stamps head.created/modified with the current
# time unless SOURCE_DATE_EPOCH is set, so every rebuild produced a
# byte-different woff2 for an identical font — a spurious 20 KB change in the
# repo on every build, and a re-upload that busts the file's cache for no
# reason. pyftsubset runs in a subprocess, so the variable has to reach it.
os.environ.setdefault("SOURCE_DATE_EPOCH", "1700000000")   # in-process saves
ENV = dict(os.environ)                                      # and the subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "public", "assets", "fonts")
DEST = os.path.join(OUT, "vazirmatn-subset.woff2")
VENDORED = os.path.join(HERE, "original", "Vazirmatn[wght].ttf")

UNICODES = ",".join([
    "U+0020-007E",                  # ASCII — product codes, model numbers
    "U+00AB,U+00BB,U+00D7",         # « » ×
    "U+060C,U+061B,U+061F",         # ، ؛ ؟
    "U+0621-0624,U+0626-0628",      # hamza forms, alef, beh
    "U+0629",                       # ة  — typed on an Arabic keyboard
    "U+062A-063A",                  # teh .. ghain
    "U+0640-0642",                  # tatweel, feh, qaf
    "U+0643",                       # ك  — Arabic kaf, typed
    "U+0644-0648",                  # lam .. waw
    "U+0649,U+064A",                # ى ي — typed
    "U+064B-0652,U+0654",           # harakat (may appear in pasted text)
    "U+0670,U+0671",
    "U+067E,U+0686,U+0698",         # پ چ ژ
    "U+06A9,U+06AF",                # ک گ
    "U+06BE,U+06C0,U+06CC,U+06D5",  # ه-variants, ی
    "U+066A-066C",                  # ٪ ٫ ٬ — CLDR decimal/thousands
    "U+06F0-06F9",                  # ۰-۹
    "U+200C-200F",                  # ZWNJ, ZWJ, LRM, RLM
    "U+2010-2011,U+2013-2014",
    "U+2018-201A,U+201C-201E,U+2026",
    "U+2039-203A",
    "U+FDFC",                       # ﷼ rial sign
    "U+FEFF",
])


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else VENDORED
    if not os.path.isfile(src):
        print(f"source font not found: {src}\n"
              f"Get Vazirmatn v33.003 from\n"
              f"  https://github.com/rastikerdar/vazirmatn/releases/tag/v33.003\n"
              f"and place fonts/variable/Vazirmatn[wght].ttf at {VENDORED}")
        return 1
    os.makedirs(OUT, exist_ok=True)
    # Limit the weight axis to what the stylesheet actually asks for. The
    # upstream variable font carries wght 100-900; DESIGN.md §4 allows three
    # weights, 200/400/800, and nothing on the site requests anything outside
    # that. Shipping deltas for 100-200 and 800-900 is paying to interpolate
    # weights no rule can reach. 57.1 -> 54.3 KB.
    #
    # (Three static cuts were measured as the alternative and are worse: 24.0
    # + 23.7 + 24.4 = 72.1 KB across three requests, against 54.3 in one. The
    # variable font stays.)
    limited = os.path.join(OUT, "_vazirmatn-wght200-800.ttf")
    subprocess.run(["fonttools", "varLib.instancer", src, "wght=200:800",
                    "-o", limited], check=True, env=ENV, capture_output=True)
    cmd = [
        "pyftsubset", limited,
        f"--output-file={DEST}", "--flavor=woff2",
        f"--unicodes={UNICODES}",
        "--layout-features=*",            # keep Arabic shaping (init/medi/fina/rlig...)
        "--name-IDs=0,1,2,3,4,5,6,13,14", # keep the OFL copyright/licence records
        "--drop-tables+=DSIG",
    ]
    subprocess.run(cmd, check=True, env=ENV)
    os.remove(limited)
    print(f"wrote {DEST}  {os.path.getsize(DEST)/1024:.1f} KB")
    # SIL OFL 1.1 requires the licence to travel with the font.
    lic_src = os.path.join(HERE, "original", "OFL.txt")
    if not os.path.isfile(lic_src):
        print(f"ERROR: {lic_src} is missing. SIL OFL 1.1 requires the licence "
              f"to ship with the font; refusing to build without it.")
        return 1
    shutil.copy(lic_src, os.path.join(OUT, "OFL-Vazirmatn.txt"))
    print(f"wrote {os.path.join(OUT, 'OFL-Vazirmatn.txt')}")
    return build_display()


# --------------------------------------------------------------- display face
# Lalezar — the display face named in DESIGN.md §3. One static weight, used
# only for h1, section heads and the board's headline figure, so it needs the
# Persian alphabet and the digits and nothing else: no Arabic look-alikes (you
# cannot type into a heading), no harakat, no Latin (ASMCO is set in Vazirmatn).
# That takes the woff2 to ~19 KB, which is what makes a second face affordable
# at all on this page budget.
LALEZAR_SRC = os.path.join(HERE, "original", "Lalezar-Regular.ttf")
LALEZAR_DEST = os.path.join(OUT, "lalezar-display.woff2")
LALEZAR_UNICODES = ",".join([
    "U+0020",
    "U+00AB,U+00BB",                # « »
    "U+060C,U+061F",                # ، ؟
    "U+0621-0628",                  # hamza forms, alef, beh
    "U+062A-063A",                  # teh .. ghain
    "U+0640-0642",                  # tatweel, feh, qaf
    "U+0644-0648",                  # lam .. waw
    "U+064A",                       # ي
    "U+066A-066C",                  # ٪ ٫ ٬ — percent, CLDR decimal/thousands
    "U+067E,U+0686,U+0698",         # پ چ ژ
    "U+06A9,U+06AF",                # ک گ
    "U+06CC",                       # ی
    "U+06F0-06F9",                  # ۰-۹
    "U+200C",                       # ZWNJ — see add_zwnj()
])


def add_zwnj(src, dst):
    """Give Lalezar a zero-width U+200C glyph.

    Upstream Lalezar has no ZWNJ in its cmap. ZWNJ is load-bearing in Persian —
    «دسته‌بندی» without it joins into a different word — and while the character
    is a formatting control, leaving it unmapped hands the shaping of that one
    position to a fallback face, which in Chromium on Android can break the
    surrounding cursive join. Mapping it to an empty zero-advance glyph keeps
    the whole run inside one font.
    """
    from fontTools.ttLib import TTFont
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    f = TTFont(src)
    name = "uni200C"
    if name not in f.getGlyphOrder():
        order = f.getGlyphOrder() + [name]
        f.setGlyphOrder(order)
        f.glyphOrder = order
        f["glyf"].glyphOrder = order
        f["glyf"].glyphs[name] = TTGlyphPen(None).glyph()
        f["hmtx"].metrics[name] = (0, 0)
        for t in f["cmap"].tables:
            if t.isUnicode():
                t.cmap[0x200C] = name
    f.save(dst)


def build_display():
    if not os.path.isfile(LALEZAR_SRC):
        print(f"display source not found: {LALEZAR_SRC}\n"
              f"Get Lalezar-Regular.ttf from\n"
              f"  https://github.com/google/fonts/tree/main/ofl/lalezar")
        return 1
    tmp = os.path.join(OUT, ".lalezar-zwnj.ttf")
    add_zwnj(LALEZAR_SRC, tmp)
    subprocess.run([
        "pyftsubset", tmp,
        f"--output-file={LALEZAR_DEST}", "--flavor=woff2",
        f"--unicodes={LALEZAR_UNICODES}",
        # Only the lookups Persian shaping actually needs. Dropping aalt/dlig
        # saves ~5 KB and neither fires in any string we set in this face.
        "--layout-features=ccmp,init,medi,fina,rlig,locl,liga",
        "--name-IDs=0,1,2,3,4,5,6,13,14",
        "--drop-tables+=DSIG",
    ], check=True, env=ENV)
    os.remove(tmp)
    print(f"wrote {LALEZAR_DEST}  {os.path.getsize(LALEZAR_DEST)/1024:.1f} KB")
    lic = os.path.join(HERE, "original", "OFL-Lalezar.txt")
    if not os.path.isfile(lic):
        print(f"ERROR: {lic} is missing. SIL OFL 1.1 requires the licence to "
              f"ship with the font; refusing to build without it.")
        return 1
    shutil.copy(lic, os.path.join(OUT, "OFL-Lalezar.txt"))
    print(f"wrote {os.path.join(OUT, 'OFL-Lalezar.txt')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
