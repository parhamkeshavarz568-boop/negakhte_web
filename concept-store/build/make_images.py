#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Masters -> the renditions the site ships. Incremental: a rendition is only
rebuilt when its master is newer, so after the first run this takes seconds.

    python build/make_images.py           # only what changed
    python build/make_images.py --all     # everything

Three cuts of every photo in the catalogue:

  card   4:5 crop, 360 / 540 / 720 wide. Every grid tile is 4:5 so a shelf of
         sixty pieces reads as one shelf. The masters come in four ratios (4:5,
         3:4, 2:3, 9:16), so a fixed centre-crop would behead the taper candles
         and the jewellery busts. The window is placed where the OBJECT is:
         pixels whose colour departs from the beige of the set, ignoring
         the window-shadows, which shift lightness but barely shift hue.
  full   the uncropped photo, 1080 wide (or the master's width if smaller),
         for the product page — where the tall bouquets need their full height.
  og     480x600 JPEG for link previews. Telegram, WhatsApp and Instagram DMs
         are where these links get shared, and not all of them read AVIF/WebP.

AVIF first, WebP as the fallback — WebP has been in every Android WebView and
every Safari since 14, so no JPEG layer for the page itself.

Writes build/data/images.json: for every photo, the crop box and the exact
pixel size of each rendition, so every <img> ships width/height and the grid
never shifts as images arrive.
"""
import json, os, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(HERE, "original", "photos")
OUT = os.path.join(os.path.dirname(HERE), "public", "assets", "img")
DATA = os.path.join(HERE, "data")

CARD_W = (360, 540, 720)
FULL_W = 1080
OG = (480, 600)
AR = 0.8                      # 4:5
AVIF = dict(quality=52, speed=6)
WEBP = dict(quality=78, method=6)


def short(photo):
    """'candle/04cda65f-560d-…' -> '04cda65f' — the public filename stem."""
    return photo.split("/")[1][:8]


def subject_window(im, ar=AR):
    W, H = im.size
    small = im.resize((max(1, W // 8), max(1, H // 8)))
    lab = np.asarray(small.convert("LAB"), dtype=np.float32)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    e = np.sqrt((a - np.median(a)) ** 2 + (b - np.median(b)) ** 2)
    e += np.clip(np.median(L) - L - 60, 0, None) * 0.5     # black candles, not shadows
    e = np.where(e > 8, e, 0)
    if W / H > ar:                                           # too wide: crop the sides
        cw = int(H * ar)
        prof = e.sum(axis=0)
        k = max(1, int(len(prof) * cw / W))
        cs = np.convolve(prof, np.ones(k), "valid")
        if cs.max() <= 0:
            x = (W - cw) // 2
        else:
            c = (np.arange(len(cs)) - (len(cs) - 1) / 2) / max(1, (len(cs) - 1) / 2)
            x = int(np.argmax(cs / cs.max() - 0.08 * np.abs(c))) * 8
        x = min(max(0, x), W - cw)
        return (x, 0, x + cw, H)
    ch = int(W / ar)
    prof = e.sum(axis=1)
    k = max(1, int(len(prof) * ch / H))
    cs = np.convolve(prof, np.ones(k), "valid")
    if cs.max() <= 0:
        y = (H - ch) // 2
    else:
        # prefer the centred window unless the subject clearly lives elsewhere
        c = (np.arange(len(cs)) - (len(cs) - 1) / 2) / max(1, (len(cs) - 1) / 2)
        y = int(np.argmax(cs / cs.max() - 0.08 * np.abs(c))) * 8
    y = min(max(0, y), H - ch)
    return (0, y, W, y + ch)


def _save(im, stem, force):
    """Write stem.avif and stem.webp unless both are already newer than the master."""
    for ext, kw in (("avif", AVIF), ("webp", WEBP)):
        im.save(os.path.join(OUT, f"{stem}.{ext}"), ext.upper(), **kw)


def render(job):
    photo, need_full, force = job
    src = os.path.join(MASTERS, photo + ".jpg")
    s = short(photo)
    mtime = os.path.getmtime(src)
    im = Image.open(src).convert("RGB")
    W, H = im.size
    box = subject_window(im)
    crop = im.crop(box)
    rec = {"master": [W, H], "box": list(box), "card": [], "full": None, "og": None}

    def fresh(path):
        return not force and os.path.exists(path) and os.path.getmtime(path) >= mtime

    for w in CARD_W:
        w = min(w, crop.width)
        h = round(w / AR)
        stem = f"{s}-c{w}"
        if not (fresh(os.path.join(OUT, stem + ".avif")) and fresh(os.path.join(OUT, stem + ".webp"))):
            _save(crop.resize((w, h), Image.LANCZOS), stem, force)
        rec["card"].append([w, h])
    if need_full:
        w = min(FULL_W, W)
        h = round(H * w / W)
        stem = f"{s}-f{w}"
        if not (fresh(os.path.join(OUT, stem + ".avif")) and fresh(os.path.join(OUT, stem + ".webp"))):
            _save(im.resize((w, h), Image.LANCZOS), stem, force)
        rec["full"] = [w, h]
        og = os.path.join(OUT, f"{s}-og.jpg")
        if not fresh(og):
            crop.resize(OG, Image.LANCZOS).save(og, "JPEG", quality=76, optimize=True, progressive=True)
        rec["og"] = list(OG)
    return photo, rec


def main():
    force = "--all" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(DATA, "products.source.json"), encoding="utf-8") as f:
        products = json.load(f)["products"]
    jobs = {}
    for p in products:
        if not p.get("category"):
            continue
        need_full = p["status"] != "sold"           # sold pieces have no product page
        jobs[p["photo"]] = jobs.get(p["photo"], False) or need_full
    stems = {}
    for photo in jobs:
        stems.setdefault(short(photo), []).append(photo)
    clash = {k: v for k, v in stems.items() if len(v) > 1}
    if clash:
        raise SystemExit(f"filename stems collide: {clash}")
    with Pool() as pool:
        results = dict(pool.map(render, [(ph, nf, force) for ph, nf in sorted(jobs.items())]))
    # drop renditions nothing refers to any more (a photo swapped or removed)
    keep = set()
    for ph, r in results.items():
        s = short(ph)
        keep |= {f"{s}-c{w}.{e}" for w, _ in r["card"] for e in ("avif", "webp")}
        if r["full"]:
            keep |= {f"{s}-f{r['full'][0]}.{e}" for e in ("avif", "webp")} | {f"{s}-og.jpg"}
    orphans = [f for f in os.listdir(OUT) if f not in keep]
    for f in orphans:
        os.remove(os.path.join(OUT, f))
    with open(os.path.join(DATA, "images.json"), "w", encoding="utf-8") as f:
        json.dump(dict(sorted(results.items())), f, indent=1)
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"{len(results)} photos, {len(keep)} files, {total / 1e6:.1f} MB"
          + (f", removed {len(orphans)} orphans" if orphans else ""))


if __name__ == "__main__":
    main()
