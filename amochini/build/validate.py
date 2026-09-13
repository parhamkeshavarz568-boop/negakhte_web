#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check the built site: links, assets, SEO tags, structured data, Persian text."""
import os, re, json, sys, collections, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public")
errors, warns, info = [], [], []


def walk_html():
    for dp, _dn, fn in os.walk(OUT):
        for f in fn:
            if f.endswith(".html"):
                p = os.path.join(dp, f)
                yield "/" + os.path.relpath(p, OUT).replace(os.sep, "/"), p


def exists(url):
    """Does a site-root-relative URL resolve to a real file?"""
    u = url.split("#")[0].split("?")[0]
    if not u.startswith("/"):
        return None
    p = os.path.join(OUT, u.lstrip("/"))
    if u.endswith("/"):
        return os.path.isfile(os.path.join(p, "index.html"))
    return os.path.isfile(p)


def main():
    docs = list(walk_html())
    info.append(f"{len(docs)} HTML documents")

    all_links = collections.Counter()
    inbound = collections.Counter()
    titles, descs, canons = {}, {}, {}

    for url, path in docs:
        s = open(path, encoding="utf-8").read()
        page = "/" + os.path.dirname(os.path.relpath(path, OUT)).replace(os.sep, "/")
        page = (page.rstrip("/") + "/") if page != "/." else "/"
        if page == "/./":
            page = "/"

        # --- required head tags ---
        for tag, pat in [
            ("title", r"<title>(.*?)</title>"),
            ("meta description", r'<meta name="description" content="(.*?)"'),
            ("canonical", r'<link rel="canonical" href="(.*?)"'),
            ("og:title", r'<meta property="og:title"'),
            ("og:image", r'<meta property="og:image"'),
            ("viewport", r'name="viewport"'),
        ]:
            if not re.search(pat, s, re.S):
                errors.append(f"{url}: missing {tag}")

        m = re.search(r"<title>(.*?)</title>", s, re.S)
        if m:
            t = html.unescape(m.group(1)).strip()
            titles.setdefault(t, []).append(url)
            if len(t) > 70:
                warns.append(f"{url}: title {len(t)} chars, may truncate — {t[:60]}…")
        m = re.search(r'<meta name="description" content="(.*?)">', s, re.S)
        if m:
            d = html.unescape(m.group(1)).strip()
            descs.setdefault(d, []).append(url)
            if len(d) > 165:
                warns.append(f"{url}: description {len(d)} chars, may truncate")
            if len(d) < 60:
                warns.append(f"{url}: description only {len(d)} chars")
        m = re.search(r'<link rel="canonical" href="(.*?)"', s)
        if m:
            canons[url] = m.group(1)

        # --- exactly one h1 ---
        h1s = re.findall(r"<h1[^>]*>", s)
        if len(h1s) != 1:
            errors.append(f"{url}: {len(h1s)} <h1> tags (want exactly 1)")

        # --- lang/dir ---
        if 'lang="fa-IR"' not in s or 'dir="rtl"' not in s:
            errors.append(f"{url}: missing lang=fa-IR or dir=rtl")

        # --- JSON-LD parses ---
        for block in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                obj = json.loads(block)
            except Exception as ex:
                errors.append(f"{url}: JSON-LD does not parse — {ex}")
                continue
            if "@context" not in obj:
                errors.append(f"{url}: JSON-LD block missing @context")
            if obj.get("@type") == "Product":
                off = obj.get("offers")
                if off:
                    if not isinstance(off.get("price"), int):
                        errors.append(f"{url}: Product price is not an integer")
                    if off.get("priceCurrency") != "IRR":
                        errors.append(f"{url}: priceCurrency != IRR")
                    # Persian digits must never leak into schema
                    if re.search(r"[۰-۹]", json.dumps(off, ensure_ascii=False)):
                        errors.append(f"{url}: Persian digits inside Offer JSON-LD")
                for req in ("name", "sku", "image", "description", "brand"):
                    if req not in obj:
                        errors.append(f"{url}: Product missing {req}")

        # --- images have dimensions + alt ---
        for img in re.findall(r"<img\b[^>]*>", s):
            if "alt=" not in img:
                errors.append(f"{url}: <img> without alt — {img[:70]}")
            if "width=" not in img or "height=" not in img:
                warns.append(f"{url}: <img> without width/height (CLS) — {img[:60]}")

        # --- collect links ---
        for href in re.findall(r'href="([^"]+)"', s):
            if href.startswith(("http", "mailto:", "tel:", "#", "data:")):
                continue
            all_links[href] += 1
            if href.startswith("/"):
                inbound[href.split("#")[0].split("?")[0]] += 1
        for src in re.findall(r'(?:src|srcset|imagesrcset)="([^"]+)"', s):
            for part in src.split(","):
                u = part.strip().split(" ")[0]
                if u.startswith("/"):
                    all_links[u] += 1

    # --- resolve every internal link ---
    missing = collections.Counter()
    for link, n in all_links.items():
        if link.startswith("/") and exists(link) is False:
            missing[link] += n
    for link, n in missing.most_common():
        errors.append(f"BROKEN LINK ({n}x): {link}")

    # --- duplicate titles / descriptions ---
    for t, us in titles.items():
        if len(us) > 1:
            errors.append(f"DUPLICATE TITLE on {len(us)} pages: {t[:60]}… {us[:3]}")
    for d, us in descs.items():
        if len(us) > 1:
            errors.append(f"DUPLICATE DESCRIPTION on {len(us)} pages: {us[:3]}")

    # --- orphan pages (no inbound internal link) ---
    prods = json.load(open(os.path.join(ROOT, "build", "data", "products.json"),
                           encoding="utf-8"))
    orphans = [p["url"] for p in prods if inbound.get(p["url"], 0) == 0]
    if orphans:
        errors.append(f"{len(orphans)} ORPHAN product pages (no inbound link): {orphans[:5]}")
    else:
        info.append("0 orphan pages — every product is linked from somewhere")

    # --- sitemap agrees with what exists ---
    sm = open(os.path.join(OUT, "sitemap.xml"), encoding="utf-8").read()
    locs = re.findall(r"<loc>(.*?)</loc>", sm)
    info.append(f"sitemap lists {len(locs)} URLs")
    for loc in locs:
        p = loc.split("amochini.ir")[-1]
        if exists(p) is False:
            errors.append(f"sitemap lists a URL that does not exist: {p}")
    built = {u.replace("/index.html", "/") for u, _ in docs}
    built = {("/" if u == "/index.html" else u) for u in built}
    smpaths = {l.split("amochini.ir")[-1] for l in locs}
    notin = built - smpaths - {"/404.html"}
    if notin:
        warns.append(f"{len(notin)} built pages absent from sitemap: {sorted(notin)[:5]}")

    # --- Arabic character contamination in visible Persian ---
    bad = {"ي": "U+064A Arabic yeh", "ك": "U+0643 Arabic kaf", "ة": "U+0629 teh marbuta"}
    for url, path in docs:
        s = open(path, encoding="utf-8").read()
        for ch, label in bad.items():
            if ch in s:
                errors.append(f"{url}: contains {label} ({ch}) — should be the Persian form")

    # --- assets present ---
    for a in ["assets/css/site.css", "assets/js/site.js",
              "assets/fonts/vazirmatn-subset.woff2", "robots.txt", "sitemap.xml",
              "search-index.json", "site.webmanifest", ".htaccess",
              "favicon.svg", "favicon.ico", "apple-touch-icon.png",
              "icon-192.png", "icon-512.png", "404.html"]:
        if not os.path.isfile(os.path.join(OUT, a)):
            errors.append(f"MISSING ASSET: {a}")

    # --- report ---
    print("=" * 66)
    for i in info:
        print("  ·", i)
    print("=" * 66)
    if errors:
        print(f"\n{len(errors)} ERROR(S):")
        for x in errors[:60]:
            print("   ✗", x)
        if len(errors) > 60:
            print(f"   … and {len(errors)-60} more")
    if warns:
        print(f"\n{len(warns)} WARNING(S):")
        agg = collections.Counter(re.sub(r"^/\S+: ", "", w) for w in warns)
        for w, n in agg.most_common(15):
            print(f"   ! ({n}x) {w[:110]}")
    if not errors:
        print("\n✓ no errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
