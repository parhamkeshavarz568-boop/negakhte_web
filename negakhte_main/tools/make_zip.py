#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The site, zipped for sending or uploading.

    python tools/make_zip.py [out.zip]        (default: dist/negakhte-main.zip)

Only what the pages load goes in: the two pages, their stylesheet, script,
font, icons and the photographs they actually reference. The design notes,
the master images and these tools stay out. The zip's root is the site's
root: unzip it into the web folder and home.html is at /home.html.
"""
import os, re, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGES = ["home.html", "index.html"]
TOP = PAGES + ["favicon.svg", "robots.txt", "site.webmanifest"]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist", "negakhte-main.zip"))
    files = set(TOP)
    # the shared assets: everything directly in assets/ (pictures are chosen below)
    for f in os.listdir(os.path.join(ROOT, "assets")):
        if os.path.isfile(os.path.join(ROOT, "assets", f)):
            files.add(f"assets/{f}")
    # every photograph a page names, in src, srcset or a meta tag
    for page in PAGES:
        text = open(os.path.join(ROOT, page), encoding="utf-8").read()
        files.update(re.findall(r"assets/img/[\w.-]+\.(?:avif|webp|jpg|png)", text))
    missing = sorted(f for f in files if not os.path.isfile(os.path.join(ROOT, f)))
    if missing:
        sys.exit("missing files: " + ", ".join(missing))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(files):
            z.write(os.path.join(ROOT, f), f)
    size = os.path.getsize(out)
    print(f"{len(files)} files -> {out} ({size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
