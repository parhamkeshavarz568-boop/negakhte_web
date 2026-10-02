#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the self-hosted font subset.

    python build/make_font.py

One family for everything: Estedad (Amin Abedi, OFL), variable 100–900.
The design sets very thin headlines against one heavy word, so a single
family does all of it: Thin 100 to Black 800, with Light 300 for titles,
Medium 500 for names and SemiBold 600 for prices. It covers Latin too, so
codes (S-10) and brand names (Aroma Fusion) match the Persian.
Chosen after setting nine Persian faces side by side on the real headline.

Why self-hosted: Google Fonts and the jsDelivr/cdnjs/unpkg CDNs sit behind
networks that are SNI-filtered in Iran, and a stalled font request does not
fail fast — it holds up first paint. Zero third-party requests.

The subset is the Persian alphabet plus the Arabic look-alikes a non-Persian
keyboard produces, Persian and ASCII digits, and ASCII. OFL 1.1 requires the
licence to travel with the font, so it is copied next to the woff2. The
release ships no licence file; OFL-Estedad.txt is the standard OFL text under
the copyright line from the font's own name table.
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
    ("Estedad[wght].ttf", "estedad-subset.woff2", "OFL-Estedad.txt"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    keep = {d for _, d, _ in FONTS} | {l for _, _, l in FONTS}
    for f in os.listdir(OUT):
        if f not in keep:
            os.remove(os.path.join(OUT, f))
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
