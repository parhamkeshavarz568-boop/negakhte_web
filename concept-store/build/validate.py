#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check the built site in public/. Run after every build; it must end with
"build is valid".

    python build/validate.py

Errors (exit 1) are things that are wrong today. Launch blockers are things
that are not known yet — the shop's name, its contact channels, its domain —
and are listed on every run until they are filled in site_config.py. They do
not fail the build, so the site can be previewed, but the site must not go
live while any are listed.
"""
import html.parser, json, os, re, sys
from collections import Counter

import catalog as CAT
from site_config import SITE, CONTACT

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(os.path.dirname(HERE), "public")
errors, warnings = [], []


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.imgs, self.h1, self.text, self.ld = [], [], 0, [], []
        self.title = self.desc = None
        self.lang = self.dir = None
        self._in = None
        self._deco = False          # inside <picture class="deco">: a mood image, alt="" is right

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang, self.dir = a.get("lang"), a.get("dir")
        for k in ("href", "src"):
            if a.get(k):
                self.refs.append((tag, a[k]))
        for k in ("srcset",):
            if a.get(k):
                self.refs += [(tag, part.strip().split(" ")[0]) for part in a[k].split(",")]
        if tag == "picture":
            self._deco = "deco" in (a.get("class") or "").split()
        if tag == "img":
            a["_deco"] = self._deco
            self.imgs.append(a)
        if tag == "h1":
            self.h1 += 1
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content")
        if tag in ("title", "script", "style"):
            self._in = (tag, a.get("type"))

    def handle_endtag(self, tag):
        self._in = None
        if tag == "picture":
            self._deco = False

    def handle_data(self, data):
        if self._in and self._in[0] == "title":
            self.title = data
        elif self._in and self._in[1] == "application/ld+json":
            self.ld.append(data)
        elif not self._in:
            self.text.append(data)


def html_files():
    for dp, _, fns in os.walk(PUBLIC):
        for fn in fns:
            if fn.endswith(".html"):
                yield os.path.join(dp, fn)


BASE = "/" + (SITE.get("base") or "/").strip("/")
BASE = "" if BASE == "/" else BASE


def resolve(ref):
    path = ref.split("#")[0].split("?")[0]
    if not path:
        return True
    if BASE:
        if not path.startswith(BASE + "/"):
            return False          # a root-absolute link that missed the deploy folder
        path = path[len(BASE):]
    full = os.path.join(PUBLIC, path.lstrip("/"))
    return os.path.isfile(full) or os.path.isfile(os.path.join(full, "index.html"))


ALLOWED_EXTERNAL = ("https://ig.me/", "https://t.me/", "https://wa.me/", "tel:")


def luminance(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    with open(os.path.join(HERE, "data", "products.source.json"), encoding="utf-8") as f:
        products = [p for p in json.load(f)["products"] if p.get("category")]
    pages = {}
    titles = Counter()
    for fp in html_files():
        rel = "/" + os.path.relpath(fp, PUBLIC).replace(os.sep, "/")
        with open(fp, encoding="utf-8") as f:
            src = f.read()
        p = Page()
        p.feed(src)
        pages[rel] = (p, src)
        titles[p.title] += 1
        if p.lang != "fa" or p.dir != "rtl":
            errors.append(f"{rel}: <html> must be lang=fa dir=rtl")
        if p.h1 != 1:
            errors.append(f"{rel}: {p.h1} <h1> (want exactly 1)")
        if not p.title or not p.desc:
            errors.append(f"{rel}: missing <title> or meta description")
        for tag, ref in p.refs:
            if ref.startswith(("http://", "https://", "tel:", "mailto:")):
                if not ref.startswith(ALLOWED_EXTERNAL) and not (SITE["url"] and ref.startswith(SITE["url"])):
                    errors.append(f"{rel}: third-party reference {ref}")
            elif ref.startswith("#"):
                continue
            elif not resolve(ref):
                errors.append(f"{rel}: broken {tag} {ref}")
        for im in p.imgs:
            if im.get("alt") is None or (not im.get("alt") and not im["_deco"]):
                errors.append(f"{rel}: <img> without alt ({im.get('src')}) — only mood images may have alt=\"\"")
            if not (im.get("width") and im.get("height")):
                errors.append(f"{rel}: <img> without width/height ({im.get('src')}) — layout shift")
        text = "".join(p.text)
        bad = re.findall(r"[يك]", text)
        if bad:
            errors.append(f"{rel}: Arabic ي/ك in visible text — Persian uses ی/ک")
        if re.search(r"[0-9]", re.sub(r"[A-Za-z]+[\w\- ]*|S-\d+|[A-Z]-\d\d", "", text)):
            warnings.append(f"{rel}: Latin digits in Persian text")
        for block in p.ld:
            try:
                json.loads(block)
            except ValueError as e:
                errors.append(f"{rel}: JSON-LD does not parse: {e}")

    for t, n in titles.items():
        if n > 1:
            errors.append(f"{n} pages share the title «{t}»")

    # every piece for sale has its page, showing the catalogue's price exactly
    for pr in products:
        url = f"/{pr['category']}/{pr['code'].lower()}/index.html"
        if pr["status"] == "sold":
            if url in pages:
                errors.append(f"{pr['code']} is sold but has a page")
            continue
        if url not in pages:
            errors.append(f"{pr['code']}: no page at {url}")
            continue
        src = pages[url][1]
        if pr["status"] == "available":
            want = CAT.toman(pr["price_toman"])
            m = re.search(r'class="prod-price"><span class="pr">([^<]+) <small>تومان', src)
            if not m or m.group(1) != want:
                errors.append(f"{pr['code']}: page shows {m.group(1) if m else 'no price'}, catalogue says {want}")
        if pr["code"] not in src:
            errors.append(f"{pr['code']}: code not shown on its page")

    # every section lists exactly its pieces
    for c in CAT.CATEGORIES:
        src = pages.get(f"/{c['slug']}/index.html", (None, ""))[1]
        want = sum(1 for p in products if p["category"] == c["slug"])
        got = src.count('<li class="item')
        if got != want:
            errors.append(f"/{c['slug']}/ shows {got} cards, catalogue has {want}")

    # colour pairs that carry text — WCAG AA 4.5:1
    css = open(os.path.join(HERE, "assets", "site.css"), encoding="utf-8").read()
    tok = {k: v.lower() for k, v in re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", css)}
    # every pair that carries text, on every ground it appears on
    for fg, bg in (("ink", "paper"), ("ink-2", "paper"), ("ink", "stone"), ("ink-2", "stone"),
                   ("gold-ink", "paper"), ("ox", "paper"), ("paper", "ox"), ("paper", "ox-deep"),
                   ("paper", "ink"), ("on-ink", "ink"), ("gold", "ink")):
        r = contrast(tok[fg], tok[bg])
        if r < 4.5:
            errors.append(f"contrast --{fg} on --{bg} is {r:.2f}:1 (< 4.5)")

    # the server config ships, and its 404 rule points inside the deploy folder
    ht = os.path.join(PUBLIC, ".htaccess")
    if not os.path.isfile(ht):
        errors.append("public/.htaccess missing")
    elif f"ErrorDocument 404 {BASE}/404.html" not in open(ht, encoding="utf-8").read():
        errors.append(".htaccess 404 rule does not match SITE['base']")

    blockers = []
    if not SITE.get("launch"):
        blockers.append("preview mode: every page says noindex — site_config.SITE['launch'] = True on launch day")
    if SITE.get("name_is_placeholder"):
        blockers.append(f"shop name is a placeholder («{SITE['name_fa']}») — site_config.SITE")
    if not any(CONTACT[k] for k in ("instagram", "telegram", "whatsapp", "phone")):
        blockers.append("no contact channel — every order button is dead — site_config.CONTACT")
    if not SITE["url"]:
        blockers.append("no domain — no canonical, no sitemap, no structured data — site_config.SITE['url']")
    if not CONTACT["address"]:
        blockers.append("no address (fine if there is no shop to visit) — site_config.CONTACT['address']")
    with open(os.path.join(HERE, "data", "products.source.json"), encoding="utf-8") as f:
        raw = json.load(f)
    guessed = [p["code"] for p in raw["products"] if p.get("name_from_photo")]
    if guessed:
        blockers.append(f"names read from the photo, not the list — confirm: {', '.join(guessed)}")

    n_pages = len(pages)
    for w in sorted(set(warnings))[:10]:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"\n{n_pages} pages checked, {len(errors)} errors")
    if blockers:
        print("\nLaunch blockers (fine for preview, not for going live):")
        for b in blockers:
            print("  -", b)
    if errors:
        return 1
    print("\nbuild is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
