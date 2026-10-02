#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docs/unassigned-photos.jpg — the photos that came in the zips but are not the
visible photo of any row in the lists, numbered to match docs/REVIEW-FA.md.

    python build/review_sheet.py
"""
import json, os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "docs", "unassigned-photos.jpg")


def main():
    with open(os.path.join(HERE, "data", "products.source.json"), encoding="utf-8") as f:
        un = json.load(f)["unassigned_photos"]
    W, H, cols, pad = 220, 275, 5, 30
    sheet = Image.new("RGB", (cols * W, ((len(un) + cols - 1) // cols) * (H + pad)), "#f5eee4")
    d = ImageDraw.Draw(sheet)
    for i, u in enumerate(un):
        im = Image.open(os.path.join(HERE, "original", "photos", u["photo"] + ".jpg")).convert("RGB")
        im.thumbnail((W - 10, H - 6))
        x, y = (i % cols) * W, (i // cols) * (H + pad)
        sheet.paste(im, (x + (W - im.width) // 2, y + 4))
        d.text((x + 8, y + H + 4), f"#{i + 1}  {u['photo'].split('/')[1][:8]}", fill="#2a2119")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT, quality=80, optimize=True)
    print(f"{len(un)} photos -> {OUT} ({os.path.getsize(OUT) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
