#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prove the font subset can actually render every string the site shows.

A cmap-only check is not enough: a subset can list a codepoint and still map
it to an empty or missing glyph. This resolves each character to a real glyph
and asserts the glyph exists and is not .notdef.
"""
import os, sys, json
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(os.path.dirname(HERE), "public", "assets", "fonts",
                    "vazirmatn-subset.woff2")

# Strings that must render. Deliberately includes the cases that break a
# Persian-only subset: Latin product codes, ASCII digits, the ZWNJ-joined
# brand names, Persian digits, and a plain space.
SAMPLES = [
    "ام‌وی‌ام", "کی‌ام‌سی", "دیسک چرخ", "لنت ترمز", "کاسه چرخ",
    "دیسک چرخ ام‌وی‌ام 33X عقب TRA-X", "AMO-001", "TRA-X", "XTRA",
    "CS35", "KMC X5", "CROSS 30H", "۲۵٬۹۸۷٬۵۰۰", "۰۹۱۲۲۶۵۰۰۷۶",
    "عمو چینی", "با عمو چینی همه قطعات پیدا میشه",
    "برلیانس 220/230", "info@amochini.ir", "«قطعات اصلی»",
    " ", "0123456789", "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
]


def main():
    f = TTFont(FONT)
    cmap = f.getBestCmap()
    order = set(f.getGlyphOrder())
    glyf = f["glyf"] if "glyf" in f else None
    bad = []
    for s in SAMPLES:
        for ch in s:
            cp = ord(ch)
            g = cmap.get(cp)
            if g is None:
                bad.append((s, ch, cp, "no cmap entry"))
            elif g not in order or g == ".notdef":
                bad.append((s, ch, cp, f"maps to {g!r}"))
    print(f"font: {FONT}")
    print(f"  size      {os.path.getsize(FONT)/1024:.1f} KB")
    print(f"  glyphs    {len(order)}")
    print(f"  cmap      {len(cmap)} codepoints")
    if "fvar" in f:
        ax = f["fvar"].axes[0]
        print(f"  variable  {ax.axisTag} {ax.minValue:.0f}-{ax.maxValue:.0f}")
    print(f"  samples   {len(SAMPLES)}")
    if bad:
        print(f"\n{len(bad)} MISSING GLYPH(S):")
        for s, ch, cp, why in bad[:30]:
            print(f"   ✗ U+{cp:04X} {ch!r} ({why}) in {s!r}")
        return 1
    print("\n✓ every character in every sample resolves to a real glyph")
    return 0


if __name__ == "__main__":
    sys.exit(main())
