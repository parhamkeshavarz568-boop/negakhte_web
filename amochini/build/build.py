#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
amochini.ir static site builder.

    python3 build/build.py

Reads build/data/products.json + build/templates + build/assets and writes the
complete uploadable site into public/.  Everything in public/ is generated —
never hand-edit it; edit the source here and rebuild.
"""
import json, os, shutil, sys, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "public")
sys.path.insert(0, HERE)

import pages as PG
from normalize import BRANDS, CATEGORIES, to_fa_digits
from site_config import SITE, CONTACT
from layout import BASE

# Build date. Passed in so the build is reproducible in CI if needed.
BUILD_DATE = os.environ.get("BUILD_DATE") or datetime.date.today().isoformat()


def write(relpath, content):
    """Write a file, creating directories. relpath is site-root relative."""
    path = os.path.join(OUT, relpath.lstrip("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def page(url, content):
    """A URL like /brake-pads/ becomes public/brake-pads/index.html."""
    rel = url.strip("/")
    return write(os.path.join(rel, "index.html") if rel else "index.html", content)


def main():
    # Image manifest, derived from what make_images.py actually produced, so a
    # template can never reference a rendition that does not exist on disk.
    imgdir = os.path.join(OUT, "assets", "img")
    man = {}
    for f in os.listdir(imgdir):
        m = re.match(r"(.+)-(\d+)\.(avif|webp|jpg)$", f)
        if not m:
            continue
        d = man.setdefault(m.group(1), {"widths": set(), "formats": set()})
        d["widths"].add(int(m.group(2)))
        d["formats"].add(m.group(3))
    from PIL import Image as _Im
    for name, d in man.items():
        w = max(d["widths"])
        with _Im.open(os.path.join(imgdir, f"{name}-{w}.jpg")) as im:
            d["ar"] = im.size[1] / im.size[0]
        d["widths"] = sorted(d["widths"])
        d["formats"] = sorted(d["formats"])
    json.dump(man, open(os.path.join(HERE, "data", "images.json"), "w"), indent=1)

    products = json.load(open(os.path.join(HERE, "data", "products.json"),
                               encoding="utf-8"))
    groups = {}
    for p in products:
        groups.setdefault(p["brand"], []).append(p)
    cats = {c: [p for p in products if p["category"] == c] for c in PG.CAT_ORDER}

    written = []

    # ---- sweep stale pages ----------------------------------------------
    # Slugs change when catalogue data is corrected. Without this, the old URL
    # stays on disk, gets uploaded, and becomes a duplicate of the new one.
    # Only generated HTML is swept; assets are left alone.
    stale_before = set()
    for dp, _dn, fn in os.walk(OUT):
        for f in fn:
            if f == "index.html" or f == "404.html":
                stale_before.add(os.path.join(dp, f))

    # ---- assets ---------------------------------------------------------
    os.makedirs(os.path.join(OUT, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assets", "js"), exist_ok=True)
    shutil.copy(os.path.join(HERE, "assets", "site.css"),
                os.path.join(OUT, "assets", "css", "site.css"))
    shutil.copy(os.path.join(HERE, "assets", "site.js"),
                os.path.join(OUT, "assets", "js", "site.js"))

    # ---- pages ----------------------------------------------------------
    written.append(("/", page("/", PG.home(products, groups))))
    for slug, items in cats.items():
        written.append((f"/{slug}/", page(f"/{slug}/",
                                          PG.category_page(slug, items, products))))
    written.append(("/brands/", page("/brands/", PG.brands_index(groups))))
    for slug, items in groups.items():
        written.append((f"/brands/{slug}/",
                        page(f"/brands/{slug}/", PG.brand_page(slug, items, products))))
    for p in products:
        written.append((p["url"], page(p["url"], PG.product_page(p, products))))
    written.append(("/about/", page("/about/", PG.about())))
    written.append(("/contact/", page("/contact/", PG.contact())))
    write("404.html", PG.not_found())

    # ---- search index ---------------------------------------------------
    # Compact on purpose: 130 entries, fetched lazily on first search keystroke.
    idx = [{"t": p["title"], "u": p["url"], "p": p["price_irr"], "k": p["search"]}
           for p in products]
    write("search-index.json", json.dumps(idx, ensure_ascii=False,
                                          separators=(",", ":")))

    # ---- sitemap --------------------------------------------------------
    # Priorities: home > categories > brands > products. Every URL is
    # canonical, absolute, and appears exactly once.
    prio = {"/": "1.0"}
    for slug in cats:
        prio[f"/{slug}/"] = "0.9"
    prio["/brands/"] = "0.8"
    for slug in groups:
        prio[f"/brands/{slug}/"] = "0.7"
    for p in products:
        prio[p["url"]] = "0.6" if p["in_stock"] else "0.4"
    prio["/about/"] = "0.3"
    prio["/contact/"] = "0.5"

    urls = "\n".join(
        f"  <url>\n    <loc>{BASE}{u}</loc>\n"
        f"    <lastmod>{BUILD_DATE}</lastmod>\n"
        f"    <changefreq>{'daily' if u in ('/',) or u.count('/') == 2 else 'weekly'}</changefreq>\n"
        f"    <priority>{prio.get(u, '0.5')}</priority>\n  </url>"
        for u, _ in written)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + urls + "\n</urlset>\n")

    # ---- robots.txt -----------------------------------------------------
    write("robots.txt", f"""User-agent: *
Allow: /

# Filter and sort states are the same products in a different order.
# They are canonicalised to the clean category URL, but keeping crawlers out
# of them saves crawl budget on a 150-page site.
Disallow: /*?q=
Disallow: /*?sort=
Disallow: /*&sort=

# Dead WordPress surface. These 410 in .htaccess; keeping crawlers out saves
# crawl budget. NOTE: /wp-content/ is deliberately NOT disallowed — the old
# product images live there and blocking it would deindex them from Google
# Images before the new pages have earned any image rankings of their own.
Disallow: /wp-admin/
Disallow: /wp-json/
Disallow: /?s=

Sitemap: {BASE}/sitemap.xml
""")

    # ---- speculation rules ----------------------------------------------
    # Instant navigation: Chrome prerenders a same-origin page once the user
    # hovers a link for ~200ms ("moderate"), so the click renders an
    # already-built page. Delivered as an external file referenced by a
    # Speculation-Rules HTTP header rather than an inline
    # <script type="speculationrules">, so the Content-Security-Policy can
    # stay at a strict script-src 'self' with no hash or 'unsafe-inline'.
    # Safe here because every page is static and there is no analytics to
    # double-count on a prerender.
    shutil.copy(os.path.join(HERE, "templates", "speculation-rules.json"),
                os.path.join(OUT, "speculation-rules.json"))

    # ---- .htaccess ------------------------------------------------------
    tpl = open(os.path.join(HERE, "templates", "htaccess.tpl"),
               encoding="utf-8").read()
    chunks = []
    for name in ("redirects.generated.conf", "redirects.manual.conf"):
        fp = os.path.join(HERE, "data", name)
        if os.path.exists(fp):
            chunks.append(open(fp, encoding="utf-8").read().rstrip())
    if chunks:
        redirects = "\n".join(chunks)
    else:
        redirects = ("  # (no per-product redirect map yet — run\n"
                     "  #  python3 build/make_redirects.py old-urls.txt\n"
                     "  #  BEFORE taking WordPress down. See docs/MIGRATION.md.)")
    write(".htaccess", tpl.replace("  # __PRODUCT_REDIRECTS__", redirects))

    # ---- web manifest ---------------------------------------------------
    write("site.webmanifest", json.dumps({
        "name": SITE["name_fa"] + " — " + SITE["tagline"],
        "short_name": SITE["name_fa"],
        "lang": "fa-IR", "dir": "rtl",
        "start_url": "/", "display": "standalone",
        "background_color": "#f2f2f2", "theme_color": SITE["theme_color"],
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ],
    }, ensure_ascii=False, indent=1))

    # ---- remove pages this build did not write ---------------------------
    kept = {p for _u, p in written}
    kept.add(os.path.join(OUT, "404.html"))
    removed = 0
    for old in sorted(stale_before - kept):
        os.remove(old)
        removed += 1
        d = os.path.dirname(old)
        while d != OUT and not os.listdir(d):
            os.rmdir(d)
            d = os.path.dirname(d)
    if removed:
        print(f"  swept {removed} stale page(s) left by a previous build")

    # ---- report ---------------------------------------------------------
    total = sum(os.path.getsize(p) for _, p in written)
    print(f"built {len(written)} pages into {OUT}")
    print(f"  home            1")
    print(f"  categories      {len(cats)}")
    print(f"  brand index     1")
    print(f"  brand pages     {len(groups)}")
    print(f"  product pages   {len(products)}")
    print(f"  about/contact   2")
    print(f"  + 404, sitemap.xml, robots.txt, search-index.json, manifest")
    print(f"  total HTML      {total/1024:.0f} KB "
          f"(avg {total/len(written)/1024:.1f} KB/page)")
    return written


if __name__ == "__main__":
    main()
