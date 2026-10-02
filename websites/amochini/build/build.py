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
import datetime as _dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# PUBLISH_DIR/PRICE_HISTORY let a throwaway preview be built elsewhere with
# different data. The real site is always public/ + data/price-history.json.
OUT = os.environ.get("PUBLISH_DIR") or os.path.join(ROOT, "public")
sys.path.insert(0, HERE)

import pages as PG
from normalize import BRANDS, CATEGORIES, to_fa_digits
from site_config import SITE, CONTACT
from layout import BASE

# Build date. Passed in so the build is reproducible in CI if needed.
BUILD_DATE = os.environ.get("BUILD_DATE") or datetime.date.today().isoformat()
# The date the about/contact copy was last edited. Bump it by hand when that
# copy changes — it must NOT track the build, or the sitemap tells crawlers
# those two pages change every deploy when they do not.
STATIC_LASTMOD = "2026-09-14"


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
    # PNG is in the list because the logo mark has an alpha channel and so has
    # no JPEG rendition — the aspect-ratio probe below reads whichever format
    # is actually present rather than assuming .jpg.
    for f in os.listdir(imgdir):
        m = re.match(r"(.+)-(\d+)\.(avif|webp|jpg|png)$", f)
        if not m:
            continue
        d = man.setdefault(m.group(1), {"widths": set(), "formats": set()})
        d["widths"].add(int(m.group(2)))
        d["formats"].add(m.group(3))
    from PIL import Image as _Im
    for name, d in man.items():
        w = max(d["widths"])
        probe = next(os.path.join(imgdir, f"{name}-{w}.{ext}")
                     for ext in ("jpg", "png", "webp", "avif")
                     if os.path.exists(os.path.join(imgdir, f"{name}-{w}.{ext}")))
        with _Im.open(probe) as im:
            d["ar"] = im.size[1] / im.size[0]
        d["widths"] = sorted(d["widths"])
        d["formats"] = sorted(d["formats"])
    json.dump(man, open(os.path.join(HERE, "data", "images.json"), "w"), indent=1)

    products = json.load(open(os.path.join(HERE, "data", "products.json"),
                               encoding="utf-8"))

    # ---- attach observed price history -----------------------------------
    # Kept out of products.json so that file stays a pure catalogue: the
    # history is an independent, append-only record written by
    # snapshot_prices.py. Products with no observation get an empty stats
    # dict, and every template treats that as "no trend exists".
    import prices as PR
    histfile = (os.environ.get("PRICE_HISTORY")
                or os.path.join(HERE, "data", "price-history.json"))
    history = (json.load(open(histfile, encoding="utf-8"))
               if os.path.exists(histfile) else {})
    for prod in products:
        prod["price"] = PR.stats(history.get(prod["sku"], []))
    tracked = sum(1 for x in products if x["price"].get("points", 0) >= 2)
    obs = sum(len(v) for v in history.values())
    ix_series, ix_meta = PR.index_series(history)
    PG.PRICE_META = dict(
        observations=obs,
        tracked=tracked,
        skus=len([x for x in products if x["price"].get("points")]),
        latest=max((x["price"]["latest_date"] for x in products
                    if x["price"].get("latest_date")), default=None),
        # the exchange layer
        index=ix_meta,
        index_series=ix_series,
        breadth=PR.breadth(history),
        synthetic=os.path.exists(os.path.join(HERE, "data", "SYNTHETIC")),
    )
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
    # The stylesheet ships without its comments. The source carries a lot of
    # them on purpose — every value traces back to DESIGN.md and several rules
    # record a measurement that justifies them — but a visitor on an Iranian
    # mobile connection should not pay for the handover notes. Measured: 17.1
    # KB over the wire with comments, 11.6 KB without, on every page.
    # Deliberately a conservative strip: the stylesheet contains no data URI
    # and no string literal holding "/*", so there is nothing for this to eat.
    css = open(os.path.join(HERE, "assets", "site.css"), encoding="utf-8").read()
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    for must in ("--board:#1a150f", ".bb-photo{", "@keyframes tick-pulse",
                 ".lattice > *{", ".board-band"):
        assert must in stripped, f"comment strip broke the stylesheet: {must!r}"
    # The grey-block bug, refused at the source. Drawing a grid's rules as a
    # --rule BACKGROUND showing through a 1px gap looks identical to .lattice
    # until a row is short, and then the empty trailing slots paint as solid
    # grey rectangles. It has been found and "fixed" three times — under the
    # category grid, under the brand grid, and under the stat band, where a
    # more specific rule kept it alive after the markup had moved to .lattice.
    # Borders belong to cells. Nothing in this stylesheet may do it the other
    # way; if a grid genuinely needs a coloured ground, give it its own token
    # and update this guard deliberately.
    for rule in re.findall(r"[^{}]*\{[^{}]*\}", stripped):
        flat = rule.replace(" ", "").replace("\n", "")
        if "gap:1px" in flat and "background:var(--rule)" in flat:
            raise AssertionError(
                "grey-block pattern is back — a 1px gap over a --rule "
                f"background. Use .lattice instead:\n{rule.strip()[:200]}")
    write("assets/css/site.css", stripped)
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
    written.append(("/prices/", page("/prices/", PG.price_index(products))))
    written.append(("/about/", page("/about/", PG.about())))
    written.append(("/contact/", page("/contact/", PG.contact())))
    write("404.html", PG.not_found())

    # ---- search index ---------------------------------------------------
    # Compact on purpose: 130 entries, fetched lazily on first search keystroke.
    idx = [{"t": p["title"], "u": p["url"], "p": p["price_irr"], "k": p["search"]}
           for p in products]
    write("search-index.json", json.dumps(idx, ensure_ascii=False,
                                          separators=(",", ":")))

    # ---- machine-readable price feeds -----------------------------------
    # An exchange publishes its data. Two files, both generated from the same
    # history the pages render, so they can never disagree with the board:
    #   /prices.json  the full record — every SKU, every observation
    #   /prices.csv   the same thing for a spreadsheet
    # Latin digits and raw rial throughout: these are for machines, and the
    # Persian-digit toman rendering belongs to the pages.
    synthetic = PG.PRICE_META.get("synthetic", False)
    feed = {
        "name": "قیمت روز قطعات ترمز — عمو چینی",
        "url": PG.BASE + "/prices/",
        "currency": "IRR",
        "note": ("Prices are stored in Iranian Rial. The site displays Toman "
                 "(Rial / 10)."),
        "generated": _dt.date.today().isoformat(),
        "index": {"base_date": PG.PRICE_META["index"].get("base_date"),
                  "base_value": 100.0,
                  "method": "equal-weighted price index, carry-forward",
                  "members": PG.PRICE_META["index"].get("members", 0),
                  "series": PG.PRICE_META["index_series"]},
        "products": [
            {"sku": p["sku"], "name": p["title"], "url": PG.BASE + p["url"],
             "category": p["category"], "brand": p["brand"],
             "price_irr": p["price_irr"],
             "history": p["price"].get("history", [])}
            for p in products],
    }
    if synthetic:
        # The flag travels WITH the data. Anyone consuming the feed learns
        # what the pages say: the last point of each series is the real
        # catalogue price, the path behind it is modelled.
        feed["synthetic_history"] = True
        feed["synthetic_note"] = (
            "Historical observations are illustrative. The most recent price "
            "of every product is the real catalogue price; earlier points are "
            "modelled until real recording accumulates.")
    write("prices.json", json.dumps(feed, ensure_ascii=False,
                                    separators=(",", ":")))

    rows = ["sku,name,category,brand,date,price_irr,price_toman"]
    for p in products:
        for d, rial in p["price"].get("history", []):
            nm = p["title"].replace('"', "'")
            rows.append(f'{p["sku"]},"{nm}",{p["category"]},{p["brand"]},'
                        f'{d},{rial},{rial // 10}')
    write("prices.csv", "\n".join(rows) + "\n")

    # ---- sitemap --------------------------------------------------------
    # Every URL canonical, absolute, and present exactly once.
    #
    # lastmod is REAL, per URL, not the build date. Google uses lastmod and
    # discounts it on sites where every URL claims to have changed on every
    # deploy — which is exactly what stamping BUILD_DATE everywhere does. A
    # product page's real lastmod is the date of its most recent price
    # observation; a listing page's is the newest lastmod among its members;
    # the static pages carry the date their copy was last edited.
    #
    # `changefreq` and `priority` are deliberately absent. Google has stated
    # it ignores both, and shipping fields a consumer ignores is noise in a
    # file whose whole job is to be trusted.
    def obs_date(pr):
        return (pr["price"].get("latest_date")
                or pr.get("updated") or BUILD_DATE)

    lastmod = {}
    for pr in products:
        lastmod[pr["url"]] = obs_date(pr)
    for slug, items in cats.items():
        lastmod[f"/{slug}/"] = max((obs_date(x) for x in items),
                                   default=BUILD_DATE)
    for slug, items in groups.items():
        lastmod[f"/brands/{slug}/"] = max((obs_date(x) for x in items),
                                          default=BUILD_DATE)
    newest = max(lastmod.values(), default=BUILD_DATE)
    lastmod["/"] = newest
    lastmod["/prices/"] = newest
    lastmod["/brands/"] = newest
    # The static pages change when their copy does, not when a price does.
    lastmod["/about/"] = STATIC_LASTMOD
    lastmod["/contact/"] = STATIC_LASTMOD

    urls = "\n".join(
        f"  <url>\n    <loc>{BASE}{u}</loc>\n"
        f"    <lastmod>{lastmod.get(u, BUILD_DATE)}</lastmod>\n  </url>"
        for u, _ in written)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + urls + "\n</urlset>\n")

    # ---- IndexNow ---------------------------------------------------------
    # Bing, Yandex, Seznam, Naver and Yep take an IndexNow ping and crawl
    # within minutes instead of days. GOOGLE IGNORES IT — it has said so
    # repeatedly, so this is not a Google tactic and must not be sold as one.
    # It is here because Bing and Yandex both have real share among Iranian
    # users, and because a brand-new domain with no backlinks has nothing
    # else pulling crawlers in.
    #
    # The protocol needs the key served as a text file at the site root whose
    # body is the key itself. Then, after a deploy:
    #   curl "https://api.indexnow.org/indexnow?url={SITE}/&key={KEY}"
    # or POST the changed URL list — see docs/DEPLOY.md.
    write("e8d8143105718dd4e8f37def76cb6820.txt", "e8d8143105718dd4e8f37def76cb6820")

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
