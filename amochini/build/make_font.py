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
    cmd = [
        "pyftsubset", src,
        f"--output-file={DEST}", "--flavor=woff2",
        f"--unicodes={UNICODES}",
        "--layout-features=*",            # keep Arabic shaping (init/medi/fina/rlig...)
        "--name-IDs=0,1,2,3,4,5,6,13,14", # keep the OFL copyright/licence records
        "--drop-tables+=DSIG",
    ]
    subprocess.run(cmd, check=True)
    print(f"wrote {DEST}  {os.path.getsize(DEST)/1024:.1f} KB")
    # SIL OFL 1.1 requires the licence to travel with the font.
    lic_src = os.path.join(HERE, "original", "OFL.txt")
    if not os.path.isfile(lic_src):
        print(f"ERROR: {lic_src} is missing. SIL OFL 1.1 requires the licence "
              f"to ship with the font; refusing to build without it.")
        return 1
    shutil.copy(lic_src, os.path.join(OUT, "OFL.txt"))
    print(f"wrote {os.path.join(OUT, 'OFL.txt')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
