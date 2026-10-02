#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package public/ for the host: dist/concept-store-upload.zip

    python build/make_upload.py

The zip holds the CONTENTS of public/ — index.html and .htaccess at its root —
so extracting it inside public_html/ (or the folder set as SITE["base"]) puts
every file where it belongs. Zipping the public folder itself is the classic
mistake: the site then lives one folder too deep and nothing opens.

It runs validate.py first and refuses to package a build with errors. Launch
blockers (name, contacts, domain) do not stop it — a preview upload is fine,
and every page says noindex until SITE["launch"] is True.

Already-compressed files (images, fonts) are stored, not deflated: zipping
them again saves nothing and makes the host's "Extract" slower.
"""
import os, sys, zipfile

import validate

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(os.path.dirname(HERE), "public")
DIST = os.path.join(os.path.dirname(HERE), "dist")
OUT = os.path.join(DIST, "concept-store-upload.zip")
STORED = (".avif", ".webp", ".jpg", ".png", ".woff2")


def main():
    if validate.main() != 0:
        print("\nnot packaged: fix the errors above first")
        return 1
    os.makedirs(DIST, exist_ok=True)
    n = 0
    with zipfile.ZipFile(OUT, "w") as z:
        for dp, _, fns in os.walk(PUBLIC):
            for fn in sorted(fns):
                full = os.path.join(dp, fn)
                arc = os.path.relpath(full, PUBLIC).replace(os.sep, "/")
                kind = zipfile.ZIP_STORED if fn.lower().endswith(STORED) else zipfile.ZIP_DEFLATED
                z.write(full, arc, compress_type=kind)
                n += 1
    with zipfile.ZipFile(OUT) as z:
        names = set(z.namelist())
    for must in ("index.html", ".htaccess", "404.html", "robots.txt", "assets/site.css"):
        if must not in names:
            print(f"packaging error: {must} is not at the zip's root")
            return 1
    print(f"\n{OUT}\n{n} files, {os.path.getsize(OUT) / 1e6:.1f} MB — extract inside public_html/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
