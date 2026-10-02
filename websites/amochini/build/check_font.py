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
FONTS = os.path.join(os.path.dirname(HERE), "public", "assets", "fonts")
FONT = os.path.join(FONTS, "vazirmatn-subset.woff2")
DISPLAY = os.path.join(FONTS, "lalezar-display.woff2")

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


# The display face sets headings and the board figure only — Persian words,
# Persian digits, the CLDR separators, and ZWNJ (which upstream Lalezar does
# not have; make_font.py injects it). It never sets Latin, so Latin is
# deliberately absent from this list.
DISPLAY_SAMPLES = [
    "قیمت روز", "دسته‌بندی محصولات", "لنت ترمز", "دیسک چرخ", "کاسه چرخ",
    "خرید بر اساس خودرو", "پرسش‌های پرتکرار", "قطعات ترمز خودروهای چینی",
    "عمو چینی", "۲۵٬۹۸۷٬۵۰۰", "۰٫۱٪", "تماس با ما", "درباره ما",
    "بیشترین تغییر", "استعلام تلفنی", "۱۴۰۴", " ", "«روند»",
]


def check(path, samples, label):
    f = TTFont(path)
    cmap = f.getBestCmap()
    order = set(f.getGlyphOrder())
    glyf = f["glyf"] if "glyf" in f else None
    bad = []
    for s in samples:
        for ch in s:
            cp = ord(ch)
            g = cmap.get(cp)
            if g is None:
                bad.append((s, ch, cp, "no cmap entry"))
            elif g not in order or g == ".notdef":
                bad.append((s, ch, cp, f"maps to {g!r}"))
    print(f"{label}: {path}")
    print(f"  size      {os.path.getsize(path)/1024:.1f} KB")
    print(f"  glyphs    {len(order)}")
    print(f"  cmap      {len(cmap)} codepoints")
    if "fvar" in f:
        ax = f["fvar"].axes[0]
        print(f"  variable  {ax.axisTag} {ax.minValue:.0f}-{ax.maxValue:.0f}")
    print(f"  samples   {len(samples)}")
    if bad:
        print(f"\n{len(bad)} MISSING GLYPH(S):")
        for s, ch, cp, why in bad[:30]:
            print(f"   ✗ U+{cp:04X} {ch!r} ({why}) in {s!r}")
        return 1
    print("  ✓ every character in every sample resolves to a real glyph")
    return 0


def main():
    rc = check(FONT, SAMPLES, "text face")
    print()
    rc |= check(DISPLAY, DISPLAY_SAMPLES, "display face")
    return rc


if __name__ == "__main__":
    sys.exit(main())
