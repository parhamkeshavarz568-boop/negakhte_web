#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The owner's four price lists -> build/data/products.source.json.

    python build/import_lists.py           # refuses to overwrite an edited catalogue
    python build/import_lists.py --force   # re-import from the spreadsheets

After the first import, products.source.json is the catalogue you edit (a
price, a sale, a new piece). Re-importing throws those edits away, hence
--force.

Each list is a sheet of rows: photo | name | price. The photo is not in the
cell — it is a picture floating over the sheet, anchored to a cell, and the
spreadsheet thumbnail is a 320px copy of a photo in the matching zip. Three
things about those anchors were measured, not assumed:

1. Rows can hold a STACK of pictures. Ten SOFAL rows carry 2-9 photos piled on
   one cell; row 44 has nine. Only one is visible in Excel: the last one drawn,
   which sits on top. In every SOFAL stack that same photo is also the only one
   the owner nudged to the sheet's standard 5.2pt offset — the rest sit at 0.
   Two independent signals agree on all ten rows, and the visible photo
   matches the name every time (row 21 «دیس خرماخوری» shows the plate, not
   the candle, egg or vase under it). So: the row's photo is the top one; the
   others are recorded as unassigned, never guessed at.

2. An anchor's row is not always the row it says. Two pictures in "Other" are
   anchored to rows 5 and 10 with a 100pt offset — and those rows are exactly
   100pt tall, so the pictures start at the top of rows 6 and 11, which have
   no picture of their own. effective_row() resolves the offset against the
   real row heights instead of trusting the anchor.

3. Thumbnails are matched to the full-size masters by pixel distance, and the
   match must be one-to-one with a clear margin. The run fails loudly if a
   master is claimed twice or a match is weak.
"""
import json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import io

import catalog as CAT

HERE = os.path.dirname(os.path.abspath(__file__))
LISTS = os.path.join(HERE, "original", "lists")
PHOTOS = os.path.join(HERE, "original", "photos")
OUT = os.path.join(HERE, "data", "products.source.json")

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS = {"xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
R_EMBED = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
EMU_PER_PT = 12700

# Rows that have a price but no name. Named from what the photo shows and
# flagged `name_from_photo`, so the owner confirms them (docs/REVIEW-FA.md).
NAMED_FROM_PHOTO = {
    ("other", 12): "عطر الورا",            # ELORA bottle; same 4,550,000 as the Allure in the beauty list
    ("other", 17): "استیکر سنگ قبر",       # blue RIP headstone figure, sticker price
    ("other", 23): "استیکر",               # small figure, sticker price
    ("other", 26): "عود Aroma Fusion",     # Aroma Fusion pack, the Aroma Fusion price
}


def read_sheet(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall(M + "si"):
            shared.append("".join(t.text or "" for t in si.iter(M + "t")))
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    fmt = sheet.find(M + "sheetFormatPr")
    default_ht = float(fmt.get("defaultRowHeight", 15)) if fmt is not None else 15.0
    heights, cells = {}, {}
    for row in sheet.iter(M + "row"):
        r = int(row.get("r"))
        if row.get("ht"):
            heights[r] = float(row.get("ht"))
        for c in row.iter(M + "c"):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            v, t = c.find(M + "v"), c.get("t")
            if t == "s" and v is not None:
                val = shared[int(v.text)]
            elif t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(M + "t"))
            else:
                val = v.text if v is not None else None
            if val is not None and val.strip():
                cells.setdefault(r, {})[col] = val.strip()

    rels = ET.fromstring(z.read("xl/drawings/_rels/drawing1.xml.rels"))
    target = {r.get("Id"): os.path.basename(r.get("Target")) for r in rels}
    drawing = ET.fromstring(z.read("xl/drawings/drawing1.xml"))
    anchors = []
    for zorder, anc in enumerate(list(drawing)):
        fr, blip = anc.find("xdr:from", NS), anc.find(".//a:blip", NS)
        if fr is None or blip is None:
            continue
        anchors.append({
            "z": zorder,
            "row": int(fr.find("xdr:row", NS).text) + 1,
            "off_pt": int(fr.find("xdr:rowOff", NS).text) / EMU_PER_PT,
            "media": target[blip.get(R_EMBED)],
        })
    media = {n.split("/")[-1]: z.read(n) for n in z.namelist() if n.startswith("xl/media/")}
    return cells, anchors, media, (lambda r: heights.get(r, default_ht))


def effective_row(a, height):
    """The row the picture's top edge actually lands in."""
    r, off = a["row"], a["off_pt"]
    while off >= height(r) - 0.01:
        off -= height(r)
        r += 1
    return r


def _vec(im):
    im = im.convert("RGB")
    a = np.asarray(im.convert("L"))
    ys, xs = np.where(a < 245)                 # trim Excel's white padding
    if len(xs):
        im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    return np.asarray(im.resize((20, 25), Image.LANCZOS), dtype=np.float32) / 255.0


def match_media(collection, media):
    folder = os.path.join(PHOTOS, collection)
    masters = {os.path.splitext(f)[0]: _vec(Image.open(os.path.join(folder, f)))
               for f in sorted(os.listdir(folder)) if f.endswith(".jpg")}
    out = {}
    for name, raw in media.items():
        v = _vec(Image.open(io.BytesIO(raw)))
        scores = sorted((float(np.mean((v - mv) ** 2)), pid) for pid, mv in masters.items())
        (best, pid), (second, _) = scores[0], scores[1]
        margin = second / max(best, 1e-9)
        if best > 0.02 or margin < 1.4:
            raise SystemExit(f"{collection}/{name}: weak photo match "
                             f"(mse {best:.4f}, margin {margin:.1f}) — check it by eye")
        out[name] = pid
    claimed = {}
    for name, pid in out.items():
        if pid in claimed:
            raise SystemExit(f"{collection}: master {pid} matched by both {claimed[pid]} and {name}")
        claimed[pid] = name
    return out, set(masters)


def parse_price(raw):
    """-> (status, toman or None)"""
    if raw is None:
        return "ask", None
    s = raw.strip()
    if any(w in s for w in CAT.SOLD_WORDS):
        return "sold", None
    if CAT.DAY_PRICE.match(re.sub(r"\s+", " ", s)):
        return "day", None
    digits = re.sub(r"[.,٬\s]", "", s).translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
    if digits.isdigit():
        return "available", int(digits)
    raise SystemExit(f"unreadable price «{raw}»")


def _utf8_console():
    """Windows consoles default to cp1252, which cannot print Persian; without
    this a plain `python build/<script>.py` crashes on the first Persian line."""
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


def main():
    _utf8_console()
    if os.path.exists(OUT) and "--force" not in sys.argv:
        print(f"{OUT} exists and may hold edits. Re-run with --force to re-import.")
        return 1
    products, unassigned, log = [], [], []
    for collection, meta in CAT.COLLECTIONS.items():
        cells, anchors, media, height = read_sheet(os.path.join(LISTS, f"{collection}.xlsx"))
        to_master, masters = match_media(collection, media)
        stacks = {}
        for a in anchors:
            er = effective_row(a, height)
            if er != a["row"]:
                log.append(f"{collection} {a['media']}: anchored to row {a['row']} "
                           f"+{a['off_pt']:.0f}pt, lands in row {er}")
            stacks.setdefault(er, []).append(a)
        used, hidden = set(), []
        for r in sorted(set(cells) | set(stacks)):
            if r == 1:
                continue                            # header row
            row = cells.get(r, {})
            stack = sorted(stacks.get(r, []), key=lambda a: a["z"])
            top = stack[-1] if stack else None
            photo = to_master[top["media"]] if top else None
            if photo:
                used.add(photo)
            for a in stack[:-1]:
                hidden.append({"collection": collection, "photo": to_master[a["media"]],
                               "under_row": r, "why": "stacked under the row's visible photo"})
            raw_name, raw_price = row.get("B"), row.get("C")
            status, price = parse_price(raw_price)
            if raw_name and any(w == raw_name.strip() for w in CAT.SOLD_WORDS):
                status, raw_name = "sold", None
            name, notes = CAT.clean_name(raw_name)
            from_photo = False
            if name is None and (collection, r) in NAMED_FROM_PHOTO and status != "sold":
                name, from_photo = NAMED_FROM_PHOTO[(collection, r)], True
            if name is None and status != "sold":
                raise SystemExit(f"{collection} row {r}: no name and not sold")
            category = CAT.classify(collection, name) if name else (
                CAT.LIST_CATEGORY.get(collection))
            if category is None and status != "sold":
                raise SystemExit(f"{collection} row {r}: «{name}» fits no section")
            if not photo:
                raise SystemExit(f"{collection} row {r}: no photo")
            p = {
                "code": f"{meta['prefix']}-{r - 1:02d}",
                "list": collection, "row": r,
                "name": name, "category": category,
                "status": status, "price_toman": price,
                "photo": f"{collection}/{photo}",
            }
            if from_photo:
                p["name_from_photo"] = True
            if raw_name and notes:
                p["name_as_typed"] = raw_name.strip()
            products.append(p)
            for n in notes:
                log.append(f"{p['code']}: {n}")
        # a photo hidden in one stack may be another row's visible photo — that one is assigned
        unassigned += [h for h in hidden if h["photo"] not in used]
        for pid in sorted(masters - used - {h["photo"] for h in hidden}):
            unassigned.append({"collection": collection, "photo": pid, "under_row": None,
                               "why": "in the zip, not in the list"})

    # Sold rows that were never named stay in the catalogue — they are real pieces
    # the shop made and sold, and the section shows them as such — but uncategorised
    # sold "Other" rows have nowhere to go.
    for p in products:
        if p["category"] is None:
            log.append(f"{p['code']}: sold, unnamed, no section — kept out of the site")
    for u in unassigned:
        u["photo"] = f"{u['collection']}/{u['photo']}"

    data = {
        "_about": "The catalogue. Edit prices, status (available | ask | day | sold) and names here, "
                  "then run build.py. price_toman is in Toman. Codes never change once published.",
        "products": products,
        "unassigned_photos": unassigned,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    from collections import Counter
    print("\n".join(log))
    print(f"\n{len(products)} products  status {dict(Counter(p['status'] for p in products))}")
    print(f"sections {dict(Counter(p['category'] for p in products))}")
    print(f"{len(unassigned)} unassigned photos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
