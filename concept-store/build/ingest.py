#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bring the owner's export into the repo. Run once per new export.

    python build/ingest.py                        # reads the default Desktop folder
    python build/ingest.py "D:/path/to/export"    # or any folder with the same files

The export is four price lists (.xlsx) and four zips of photos, one pair per
collection. What this does with them:

  lists   copied byte-for-byte to build/original/lists/ under stable names.
          They are the record of what the owner supplied; import_lists.py reads
          them and nothing ever writes to them.

  photos  every PNG decoded and re-saved as a JPEG master at its native size,
          quality 90, no chroma subsampling. The PNGs are 2 MB each (400 MB in
          all) and carry nothing a JPEG at q90/4:4:4 loses at this resolution;
          the masters are ~1/6 of that. The site's renditions are made from the
          masters by make_images.py, never from the PNGs.

          Byte-identical duplicates inside a zip ("X.PNG" next to "X 2.PNG")
          are dropped by comparing decoded pixels, not filenames.

  MANIFEST.json records, for every master, the zip and filename it came from
  and the sha256 of the original bytes — so any photo on the site can be traced
  back to the file the owner sent.
"""
import hashlib, io, json, os, shutil, sys, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
LISTS = os.path.join(HERE, "original", "lists")
PHOTOS = os.path.join(HERE, "original", "photos")
DEFAULT_SRC = os.path.join(os.path.expanduser("~"), "Desktop", "consept store")

# collection key -> (zip name, xlsx name). The keys are the codes' prefixes.
EXPORT = {
    "candle":  ("Candle.zip",               "Candle_Product_List (1).xlsx"),
    "beauty":  ("Nixgel- Atr - Niura.zip",  "Nixgel_Atr_Niura_Product_List (1).xlsx"),
    "other":   ("Other.zip",                "Other_Product_List_76(AutoRecovered).xlsx"),
    "ceramic": ("SOFAL.zip",                "SOFAL_Product_List (1).xlsx"),
}

os.environ.setdefault("SOURCE_DATE_EPOCH", "1700000000")


def photo_id(name):
    """'04CDA65F-560D-4DC4-88DB-4AD84C6337BA 2.PNG' -> '04cda65f-560d-4dc4-88db-4ad84c6337ba'"""
    stem = os.path.splitext(os.path.basename(name))[0]
    return stem.split(" ")[0].lower()


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    if not os.path.isdir(src):
        print(f"export folder not found: {src}")
        return 1
    os.makedirs(LISTS, exist_ok=True)
    manifest = {}
    for key, (zname, xname) in EXPORT.items():
        shutil.copyfile(os.path.join(src, xname), os.path.join(LISTS, f"{key}.xlsx"))
        out_dir = os.path.join(PHOTOS, key)
        os.makedirs(out_dir, exist_ok=True)
        seen = {}          # pixel hash -> photo id
        kept = dropped = 0
        with zipfile.ZipFile(os.path.join(src, zname)) as z:
            for info in sorted(z.infolist(), key=lambda i: i.filename):
                n = info.filename
                if info.is_dir() or n.startswith("__MACOSX/") or "/." in n:
                    continue
                if not n.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                raw = z.read(n)
                im = Image.open(io.BytesIO(raw))
                im.load()
                im = im.convert("RGB")
                px = hashlib.sha256(im.tobytes()).hexdigest()
                pid = photo_id(n)
                if px in seen:
                    print(f"  {key}: drop duplicate {os.path.basename(n)} (= {seen[px]})")
                    dropped += 1
                    continue
                if any(v["id"] == pid for v in manifest.values()):
                    pid = pid + "-b"   # same stem, different pixels — keep both
                seen[px] = pid
                dest = os.path.join(out_dir, pid + ".jpg")
                im.save(dest, "JPEG", quality=90, subsampling=0, optimize=True)
                manifest[f"{key}/{pid}"] = {
                    "id": pid, "collection": key, "zip": zname,
                    "file": os.path.basename(n), "sha256": hashlib.sha256(raw).hexdigest(),
                    "size": list(im.size),
                }
                kept += 1
        print(f"{key:8s} {kept} masters, {dropped} duplicates dropped")
    with open(os.path.join(PHOTOS, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1, sort_keys=True)
    total = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fns in os.walk(PHOTOS) for fn in fns)
    print(f"masters: {len(manifest)} files, {total/1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
