#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the two self-hosted font subsets.

    python build/make_font.py

  Markazi Text (Borna Izadpanah, OFL) — names and headings. A text face drawn
      from Persian book typography, with the slow, inked quality of a label
      written by hand; it is what makes the site feel like a shop and not a
      catalogue. Variable 400–700.
  Vazirmatn (Saber Rastikerdar, OFL) — prices, codes, buttons, small text.
      Even, clear numerals at small sizes. Variable 100–900, same pinned
      v33.003 file the amochini site vendors.

Why self-hosted: Google Fonts and the jsDelivr/cdnjs/unpkg CDNs sit behind
networks that are SNI-filtered in Iran, and a stalled font request does not
fail fast — it holds up first paint. Zero third-party requests.

The subset is the Persian alphabet plus the Arabic look-alikes a non-Persian
keyboard produces, Persian and ASCII digits, and ASCII (codes like S-12,
brand names like Aroma Fusion). OFL 1.1 requires the licence to travel with
the font, so both licence files are copied next to the woff2 files.
"""
import os, shutil, subprocess, sys

os.environ.setdefault("SOURCE_DATE_EPOCH", "1700000000")   # byte-identical rebuilds
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "original", "fonts")
OUT = os.path.join(os.path.dirname(HERE), "public", "assets", "fonts")

UNICODES = ",".join([
    "U+0020-007E", "U+00A0", "U+00AB,U+00BB,U+00D7",
    "U+060C,U+061B,U+061F",
    "U+0621-063A", "U+0640-064A", "U+064B-0652,U+0654",
    "U+066A-066C",                   # ٪ ٫ ٬
    "U+0670,U+067E,U+0686,U+0698,U+06A9,U+06AF,U+06BE,U+06C0,U+06CC",
    "U+06F0-06F9",                   # ۰-۹
    "U+200C-200F",
    "U+2013-2014,U+2018-2019,U+201C-201D,U+2026,U+2190-2193,U+2022",
])

FONTS = [
    ("MarkaziText[wght].ttf", "markazi-subset.woff2", "OFL-MarkaziText.txt"),
    ("Vazirmatn[wght].ttf", "vazirmatn-subset.woff2", "OFL-Vazirmatn.txt"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for src, dest, lic in FONTS:
        cmd = [sys.executable, "-m", "fontTools.subset", os.path.join(SRC, src),
               f"--unicodes={UNICODES}", "--flavor=woff2",
               f"--output-file={os.path.join(OUT, dest)}",
               "--layout-features=*", "--name-IDs=*", "--name-languages=*",
               "--no-hinting", "--desubroutinize"]
        subprocess.run(cmd, check=True, env=dict(os.environ))
        shutil.copyfile(os.path.join(SRC, lic), os.path.join(OUT, lic))
        print(f"{dest}: {os.path.getsize(os.path.join(OUT, dest)) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
