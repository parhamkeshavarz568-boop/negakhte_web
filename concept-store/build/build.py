#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Write the whole site into public/ from the catalogue.

    python build/build.py

Reads  build/data/products.source.json   the catalogue (edit this)
       build/data/images.json            written by make_images.py
       build/site_config.py              name, contacts, home-page picks
Writes public/  — every page, sitemap, robots, 404. Never edit public/ by
hand; the next build overwrites it.

URL map
    /                          home
    /<section>/                eight sections, e.g. /ceramics/
    /<section>/<code>/         one page per piece that is for sale, e.g. /ceramics/s-10/
    /about/                    about, how to order, contact
    /404.html
"""
import datetime, hashlib, html, json, os, re, shutil, sys, urllib.parse

import catalog as CAT
from site_config import SITE, CONTACT, HOME, COVERS, HANDMADE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBLIC = os.path.join(ROOT, "public")
ASSETS = os.path.join(HERE, "assets")

# The deploy folder: "" when public/ is the web root, "/shop" for a subfolder.
BASE = "/" + (SITE.get("base") or "/").strip("/")
BASE = "" if BASE == "/" else BASE

esc = html.escape
Z = "‌"   # ZWNJ, for the few strings assembled from parts


# ------------------------------------------------------------------ data

def load():
    with open(os.path.join(HERE, "data", "products.source.json"), encoding="utf-8") as f:
        products = [p for p in json.load(f)["products"] if p.get("category")]
    with open(os.path.join(HERE, "data", "images.json"), encoding="utf-8") as f:
        images = json.load(f)
    for p in products:
        p["sold"] = p["status"] == "sold"
        p["url"] = f"/{p['category']}/{p['code'].lower()}/"
        p["img"] = images[p["photo"]]
    return products, {p["code"]: p for p in products}


def jalali_year(d):
    # The Persian year turns at Nowruz, 20 or 21 March.
    return d.year - 621 if (d.month, d.day) >= (3, 21) else d.year - 622


# ------------------------------------------------------------------ fragments

def asset_url(name):
    with open(os.path.join(PUBLIC, "assets", name), "rb") as f:
        return f"/assets/{name}?v={hashlib.sha256(f.read()).hexdigest()[:10]}"


def stem(p):
    return p["photo"].split("/")[1][:8]


def picture(p, kind, sizes, eager=False, cls=""):
    """<picture> with AVIF + WebP srcsets and the true pixel size on the <img>."""
    s, im = stem(p), p["img"]
    if kind == "card":
        cands = [(f"/assets/img/{s}-c{w}", w) for w, _ in im["card"]]
        w, h = im["card"][1] if len(im["card"]) > 1 else im["card"][0]
        fallback = f"/assets/img/{s}-c{w}.webp"
    else:
        w, h = im["full"]
        cands = [(f"/assets/img/{s}-f{w}", w)]
        fallback = f"/assets/img/{s}-f{w}.webp"
    avif = ", ".join(f"{u}.avif {cw}w" for u, cw in cands)
    webp = ", ".join(f"{u}.webp {cw}w" for u, cw in cands)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    alt = esc(p["name"] or CAT.CATEGORY[p["category"]]["fa"])
    return (f'<picture class="{cls}"><source type="image/avif" srcset="{avif}" sizes="{sizes}">'
            f'<img src="{fallback}" srcset="{webp}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{alt}" {load} decoding="async"></picture>')


def price_html(p, long=False):
    if p["status"] == "available":
        return f'<span class="price">{CAT.toman(p["price_toman"])} <small>تومان</small></span>'
    if p["status"] == "day":
        return f'<span class="price price-ask">{"قیمت به نرخ روز نقره" if long else "قیمت روز"}</span>'
    if p["status"] == "ask":
        return '<span class="price price-ask">قیمت را بپرسید</span>'
    return '<span class="price price-sold">فروخته شد</span>'


GRID_SIZES = "(min-width: 1240px) 280px, (min-width: 1100px) 23vw, (min-width: 700px) 31vw, 46vw"


def card(p):
    name = esc(p["name"]) if p["name"] else esc(CAT.CATEGORY[p["category"]]["fa"])
    img = picture(p, "card", GRID_SIZES, cls="card-img")
    if p["sold"]:
        named = f'<span class="card-name">{name}</span>' if p["name"] else ""
        return f'<li class="card is-sold">{img}{named}{price_html(p)}</li>'
    return (f'<li class="card"><a href="{p["url"]}">{img}<span class="card-name">{name}</span>'
            f'{price_html(p)}</a></li>')


def light(where):
    """The signature: the window's light, as it falls in every photo.

    A six-paned window (2 x 3) projected by a low sun: the panes become lit
    patches, the mullions between them stay in shade, and the whole shape leans
    the way the shadows lean in the photographs. CSS feathers its edges and
    multiplies it onto the ground."""
    pw, ph, gap = 16, 19, 3.6
    panes = "".join(
        f'<rect x="{c * (pw + gap):.1f}" y="{r * (ph + gap):.1f}" width="{pw}" height="{ph}"/>'
        for c in range(2) for r in range(3))
    w, h = 2 * pw + gap, 3 * ph + 2 * gap
    return (f'<div class="light light-{where}" aria-hidden="true">'
            f'<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">'
            f'<defs><filter id="soft-{where}" x="-30%" y="-30%" width="160%" height="160%">'
            f'<feGaussianBlur stdDeviation="1.1"/></filter></defs>'
            f'<g filter="url(#soft-{where})" transform="translate(50 50) skewX(-32) '
            f'translate({-w / 2:.2f} {-h / 2:.2f})">{panes}</g></svg></div>')


MARK = ('<svg class="mark" viewBox="0 0 24 30" aria-hidden="true">'
        '<path d="M2 29V12.5C2 6.6 6.5 2.3 12 1c5.5 1.3 10 5.6 10 11.5V29Z" fill="none" '
        'stroke="currentColor" stroke-width="1.6"/>'
        '<path d="M12 4v25M2.6 16h18.8" stroke="currentColor" stroke-width="1.2"/></svg>')


def channels():
    """[(key, label, href)] for every channel the shop has set. Order = preference."""
    c, out = CONTACT, []
    if c["instagram"]:
        out.append(("instagram", "دایرکت اینستاگرام", f"https://ig.me/m/{c['instagram']}"))
    if c["telegram"]:
        out.append(("telegram", "تلگرام", f"https://t.me/{c['telegram']}"))
    if c["whatsapp"]:
        out.append(("whatsapp", "واتساپ", f"https://wa.me/{c['whatsapp']}"))
    if c["phone"]:
        out.append(("phone", "تماس تلفنی", f"tel:{c['phone']}"))
    return out


def channel_buttons(message=None):
    chs = channels()
    if not chs:
        # Nothing configured yet: the buttons are drawn so the page can be reviewed,
        # but they go nowhere. validate.py fails the build for launch until filled.
        chs = [("instagram", "دایرکت اینستاگرام", None), ("phone", "تماس تلفنی", None)]
    out = []
    for i, (key, label, href) in enumerate(chs):
        cls = "btn btn-primary" if i == 0 else "btn"
        if href and key == "whatsapp" and message:
            href += "?text=" + urllib.parse.quote(message)
        if href:
            ext = '' if key == "phone" else ' rel="noopener" target="_blank"'
            out.append(f'<a class="{cls}" href="{esc(href)}"{ext}>{label}</a>')
        else:
            out.append(f'<a class="{cls}" aria-disabled="true" data-todo="contact">{label}</a>')
    return '<div class="channels">' + "".join(out) + "</div>"


def abs_url(path):
    return SITE["url"] + BASE + path if SITE["url"] else None


def rebase(text):
    """Pages are written with root-absolute paths (/assets/…, /candles/). When the
    site is deployed into a folder, prefix every one of them with it — href, src,
    each srcset candidate, and the prefetch rule — in one place."""
    if not BASE:
        return text
    text = re.sub(r'(href|src)="/(?!/)', rf'\1="{BASE}/', text)
    text = re.sub(r'srcset="([^"]*)"',
                  lambda m: 'srcset="' + re.sub(r'(^|,\s*)/(?!/)', lambda n: n.group(1) + BASE + "/",
                                                m.group(1)) + '"', text)
    return text.replace('"href_matches":"/*"', f'"href_matches":"{BASE}/*"')


def hl(text):
    """negakhte's highlighter: a gold bar under the lower half of the words."""
    return f'<span class="hl">{text}</span>'


def wordmark():
    return (f'<a class="wordmark" href="/">{MARK}<span>{esc(SITE["name_fa"])}</span>'
            f'<span class="diamond" aria-hidden="true"></span></a>')


# ------------------------------------------------------------------ shell

NAV = [("/#collections", "مجموعه‌ها"), ("/about/#order", "سفارش"), ("/about/", "درباره")]


def page(path, title, desc, body, *, og=None, jsonld=None, body_class="", crumbs=None):
    url = abs_url(path)
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        # the phone's browser bar takes the colour of the top of the page
        f'<meta name="theme-color" content="{"#3F1610" if "is-home" in body_class else "#F5EFE6"}">',
        '<meta name="color-scheme" content="light">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="preload" href="/assets/fonts/markazi-subset.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="/assets/fonts/vazirmatn-subset.woff2" as="font" type="font/woff2" crossorigin>',
        f'<link rel="stylesheet" href="{CSS_URL}">',
        f'<meta property="og:site_name" content="{esc(SITE["name_fa"])}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:locale" content="{SITE["locale"]}">',
        '<meta property="og:type" content="website">',
    ]
    if not SITE.get("launch"):
        head.append('<meta name="robots" content="noindex">')    # preview — see site_config
    if url:
        head.append(f'<link rel="canonical" href="{url}">')
        head.append(f'<meta property="og:url" content="{url}">')
        if og:
            head.append(f'<meta property="og:image" content="{abs_url(og)}">')
            head.append('<meta property="og:image:width" content="480">')
            head.append('<meta property="og:image:height" content="600">')
    head.append('<meta name="twitter:card" content="summary_large_image">')
    head.append('<script type="speculationrules">{"prefetch":[{"where":{"href_matches":"/*"},'
                '"eagerness":"moderate"}]}</script>')
    blocks = []
    if crumbs and SITE["url"]:
        blocks.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                       "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n,
                                            "item": abs_url(u)} for i, (u, n) in enumerate(crumbs)]})
    if jsonld and SITE["url"]:
        blocks.append(jsonld)
    for b in blocks:
        head.append('<script type="application/ld+json">'
                    + json.dumps(b, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
                    + "</script>")

    nav = "".join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    crumb_html = ""
    if crumbs:
        parts = [f'<a href="{u}">{esc(n)}</a>' for u, n in crumbs[:-1]]
        parts.append(f'<span aria-current="page">{esc(crumbs[-1][1])}</span>')
        crumb_html = '<nav class="crumbs wrap" aria-label="مسیر">' + '<span aria-hidden="true">/</span>'.join(parts) + "</nav>"

    sections = "".join(f'<li><a href="/{c["slug"]}/">{c["fa"]}</a></li>' for c in CAT.CATEGORIES)
    contact = "".join(f'<li><a href="{esc(h)}">{l}</a></li>' for _, l, h in channels())
    if CONTACT["address"]:
        contact += f'<li>{esc(CONTACT["address"])}</li>'
    if CONTACT["hours"]:
        contact += f'<li>{esc(CONTACT["hours"])}</li>'
    year = CAT.fa_digits(jalali_year(TODAY))
    foot_contact = (f'<div><h2>تماس</h2><ul>{contact}</ul></div>' if contact else "")
    return f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
{chr(10).join(head)}
</head>
<body class="{body_class}">
<a class="skip" href="#main">رفتن به محتوا</a>
<header class="masthead">
<div class="wrap masthead-in">
{wordmark()}
<nav class="nav" aria-label="اصلی">{nav}</nav>
</div>
</header>
{crumb_html}
<main id="main">
{body}
</main>
<footer class="foot">
<div class="wrap foot-in">
<div class="foot-brand">{wordmark()}
<p>{esc(SITE["tagline"])}</p></div>
<div><h2>مجموعه‌ها</h2><ul>{sections}</ul></div>
{foot_contact}
</div>
<p class="wrap foot-small">© {year} {esc(SITE["name_fa"])}</p>
</footer>
<script src="{JS_URL}" defer></script>
</body>
</html>
"""


# ------------------------------------------------------------------ pages

def for_sale(ps):
    return [p for p in ps if not p["sold"]]


def count_label(n):
    return f"{CAT.fa_digits(n)} قطعه"


def order_steps():
    return f"""<ol class="steps">
<li><span class="step-n">۱</span><h3>قطعه را انتخاب کنید</h3><p>هر قطعه یک کد دارد، مثل <bdi class="code">S-10</bdi>؛ زیر قیمتش نوشته شده.</p></li>
<li><span class="step-n">۲</span><h3>کد را بفرستید</h3><p>کد را در دایرکت یا پیام برای ما بفرستید. موجودی را همان لحظه می‌گوییم.</p></li>
<li><span class="step-n">۳</span><h3>هماهنگی ارسال</h3><p>شیوهٔ پرداخت و ارسال یا تحویل را با هم هماهنگ می‌کنیم.</p></li>
</ol>"""


def home(products, by_code):
    hero = [by_code[c] for c in HOME["hero"]]
    shelf = [by_code[c] for c in HOME["shelf"]]
    tiles = []
    for c in CAT.CATEGORIES:
        ps = [p for p in products if p["category"] == c["slug"]]
        cover = by_code[COVERS[c["slug"]]]
        tiles.append(
            f'<li class="tile"><a href="/{c["slug"]}/">'
            f'{picture(cover, "card", "(min-width: 1100px) 280px, (min-width: 700px) 23vw, 46vw", cls="tile-img")}'
            f'<span class="tile-name">{c["fa"]}</span>'
            f'<span class="tile-count">{count_label(len(for_sale(ps)))}</span></a></li>')
    total = len(for_sale(products))
    main, a, b = hero
    line = esc(SITE["tagline"])
    em = esc(SITE.get("tagline_em") or "")
    if em and em in line:
        line = line.replace(em, f"<em>{em}</em>", 1)

    def print_(p, cls, sizes, eager=False):
        return (f'<a class="print {cls}" href="{p["url"]}">{picture(p, "card", sizes, eager=eager)}'
                f'<span class="print-cap">{esc(p["name"])}</span></a>')

    # the shelf label: every section, twice over, so the strip can loop seamlessly
    labels = "".join(f"<span>{c['fa']}</span>" for c in CAT.CATEGORIES)
    body = f"""
<section class="hero on-dark">
{light("hero")}
<div class="wrap hero-in">
<div class="hero-text">
<p class="eyebrow">{"" if SITE.get("name_is_placeholder") else "کانسپت‌استور · "}دست‌ساز و انتخابی</p>
<h1 class="hero-name">{esc(SITE["name_fa"])}<span class="diamond" aria-hidden="true"></span></h1>
<p class="hero-line">{line}؛ شمع، سفال، گل بافتنی، نقره و هدیه‌های کوچک.</p>
<div class="hero-cta"><a class="btn btn-primary" href="#collections">دیدن مجموعه‌ها</a><a class="btn" href="/about/#order">چطور سفارش بدهم؟</a></div>
<p class="hero-count">{CAT.fa_digits(total)} قطعه برای فروش، در {CAT.fa_digits(len(CAT.CATEGORIES))} مجموعه</p>
</div>
<div class="hero-shelf">
{print_(main, "hero-main", "(min-width: 900px) 30vw, 88vw", eager=True)}
{print_(a, "hero-side hero-a", "(min-width: 900px) 17vw, 44vw")}
{print_(b, "hero-side hero-b", "(min-width: 900px) 16vw, 44vw")}
</div>
</div>
</section>
<div class="marquee" aria-hidden="true"><div class="marquee-track">{labels}{labels}{labels}{labels}</div></div>

<section class="wrap block" id="collections" aria-labelledby="h-collections">
<div class="block-head"><h2 id="h-collections">{hl("مجموعه‌ها")}</h2><p>هشت قفسه؛ از شمع و سفال تا عود و ادویه.</p></div>
<ul class="tiles">{"".join(tiles)}</ul>
</section>

<section class="wrap block" aria-labelledby="h-shelf">
<div class="block-head"><h2 id="h-shelf">{hl("از قفسه‌ها")}</h2><p>چند قطعه از هر مجموعه.</p></div>
<ul class="grid">{"".join(card(p) for p in shelf)}</ul>
</section>

<section class="order-band on-dark" id="order" aria-labelledby="h-order">
{light("band")}
<div class="wrap">
<div class="block-head"><h2 id="h-order">{hl("سفارش، در سه قدم")}</h2><p>سبد خرید نداریم؛ هر قطعه را با کدش سفارش می‌دهید و ما جواب می‌دهیم.</p></div>
{order_steps()}
{channel_buttons()}
</div>
</section>
"""
    store = {"@context": "https://schema.org", "@type": "Store", "name": SITE["name_fa"],
             "description": SITE["description"], "url": abs_url("/"),
             "image": abs_url(f"/assets/img/{stem(main)}-og.jpg")}
    if CONTACT["phone"]:
        store["telephone"] = CONTACT["phone"]
    if CONTACT["address"]:
        store["address"] = {"@type": "PostalAddress", "streetAddress": CONTACT["address"],
                            "addressLocality": CONTACT["city"] or "", "addressCountry": "IR"}
    return page("/", f'{SITE["name_fa"]} — {SITE["tagline"]}', SITE["description"], body,
                og=f"/assets/img/{stem(main)}-og.jpg", jsonld=store, body_class="is-home")


def section_page(c, products):
    ps = [p for p in products if p["category"] == c["slug"]]
    live, sold = for_sale(ps), [p for p in ps if p["sold"]]
    others = "".join(f'<li><a href="/{o["slug"]}/"{" aria-current=\"page\"" if o is c else ""}>{o["fa"]}</a></li>'
                     for o in CAT.CATEGORIES)
    sold_html = ""
    if sold:
        sold_html = f"""
<section class="wrap block block-sold" aria-labelledby="h-sold">
<div class="block-head"><h2 id="h-sold">{hl("به خانهٔ تازه رفتند")}</h2><p>{CAT.fa_digits(len(sold))} قطعه از این قفسه فروخته شده. اگر مشابهش را می‌خواهید، بپرسید.</p></div>
<ul class="grid grid-sold">{"".join(card(p) for p in sold)}</ul>
</section>"""
    summary = count_label(len(live)) + (f" · {CAT.fa_digits(len(sold))} فروخته‌شده" if sold else "")
    body = f"""
<header class="sec-head">
{light("head")}
<div class="wrap">
<p class="eyebrow">{summary}</p>
<h1>{hl(c["fa"])}</h1>
<p class="sec-intro">{esc(c["intro"])}</p>
</div>
</header>
<nav class="wrap chips" aria-label="مجموعه‌ها"><ul>{others}</ul></nav>
<section class="wrap block" aria-label="{c["fa"]} — برای فروش">
<ul class="grid">{"".join(card(p) for p in live)}</ul>
</section>
{sold_html}
"""
    cover = live[0] if live else ps[0]
    return page(f'/{c["slug"]}/', f'{c["fa"]} — {SITE["name_fa"]}',
                f'{c["intro"]} {count_label(len(live))} برای فروش.', body,
                og=f"/assets/img/{stem(cover)}-og.jpg" if cover["img"]["og"] else None,
                crumbs=[("/", "خانه"), (f'/{c["slug"]}/', c["fa"])])


BRANDS = (("نیکس‌ژل", "Nixgel"), ("نیورا", "Niura"), ("الورا", "ELORA"))


def product_page(p, products):
    c = CAT.CATEGORY[p["category"]]
    same = for_sale([q for q in products if q["category"] == p["category"]])
    i = same.index(p)
    related = (same[i + 1:] + same[:i])[:8]
    message = f"سلام! این قطعه را می‌خواهم:\n{p['code']} — {p['name']}"
    if SITE["url"]:
        message += "\n" + abs_url(p["url"])
    handmade = ('<li>دست‌ساز است و هر قطعه فقط یکی؛ ممکن است با عکس کمی تفاوت داشته باشد.</li>'
                if p["category"] in HANDMADE else "")
    day = ('<li>قیمت نقره هر روز تغییر می‌کند؛ قیمتِ امروز را در پیام می‌گوییم.</li>'
           if p["status"] == "day" else "")
    rel_html = ""
    if related:
        rel_html = f"""
<section class="wrap block" aria-labelledby="h-more">
<div class="block-head"><h2 id="h-more">{hl("باز هم از " + c["fa"])}</h2><p><a href="/{c["slug"]}/">همهٔ {count_label(len(same))}</a></p></div>
<ul class="grid">{"".join(card(q) for q in related)}</ul>
</section>"""
    body = f"""
<article class="wrap product">
<div class="product-photo">{picture(p, "full", "(min-width: 900px) 52vw, 100vw", eager=True)}</div>
<div class="product-info">
<p class="eyebrow"><a href="/{c["slug"]}/">{c["fa"]}</a></p>
<h1>{esc(p["name"])}</h1>
<p class="product-price">{price_html(p, long=True)}</p>
<div class="order" id="order">
<p class="code-row"><span>کد قطعه</span><bdi class="code" dir="ltr">{p["code"]}</bdi>
<button class="copy" type="button" data-copy="{esc(message)}">کپی کد و نام</button></p>
{channel_buttons(message)}
<p class="hint">کد را بفرستید؛ موجودی، پرداخت و ارسال را همان‌جا هماهنگ می‌کنیم.</p>
<button class="share" type="button" hidden data-share-title="{esc(p["name"])}">فرستادن برای یک دوست</button>
</div>
<ul class="notes">{handmade}{day}</ul>
</div>
</article>
<div class="buybar" aria-hidden="true"><div class="wrap buybar-in">{price_html(p)}<a class="btn btn-primary" href="#order" tabindex="-1">سفارش با کد <bdi dir="ltr">{p["code"]}</bdi></a></div></div>
{rel_html}
"""
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "sku": p["code"],
          "image": abs_url(f"/assets/img/{stem(p)}-f{p['img']['full'][0]}.webp"),
          "url": abs_url(p["url"]), "category": c["fa"]}
    for fa, en in BRANDS:
        if fa in p["name"]:
            ld["brand"] = {"@type": "Brand", "name": en}
    if p["status"] == "available":
        # Schema.org wants ISO 4217 and Toman has no code: publish the Rial value.
        ld["offers"] = {"@type": "Offer", "price": p["price_toman"] * 10, "priceCurrency": "IRR",
                        "availability": "https://schema.org/InStock", "url": abs_url(p["url"])}
    desc = f'{p["name"]} — {c["fa"]}، کد {p["code"]}. '
    desc += (f'{CAT.toman(p["price_toman"])} تومان.' if p["status"] == "available" else "قیمت را بپرسید.")
    return page(p["url"], f'{p["name"]} · {p["code"]} — {SITE["name_fa"]}', desc, body,
                og=f"/assets/img/{stem(p)}-og.jpg", jsonld=ld, body_class="is-product",
                crumbs=[("/", "خانه"), (f'/{c["slug"]}/', c["fa"]), (p["url"], p["name"])])


def about_page():
    contact_items = "".join(f'<li><a href="{esc(h)}">{l}</a></li>' for _, l, h in channels())
    if CONTACT["phone_display"]:
        contact_items += f'<li>تلفن: <bdi dir="ltr">{esc(CONTACT["phone_display"])}</bdi></li>'
    if CONTACT["address"]:
        contact_items += f'<li>نشانی: {esc(CONTACT["address"])}</li>'
    if CONTACT["hours"]:
        contact_items += f'<li>ساعت کار: {esc(CONTACT["hours"])}</li>'
    body = f"""
<header class="sec-head">
{light("head")}
<div class="wrap">
<p class="eyebrow">درباره</p>
<h1>{hl(esc(SITE["name_fa"]))}</h1>
<p class="sec-intro">یک فروشگاه کوچک برای چیزهایی که دوست داریم: شمع‌های دست‌ساز، سفالِ لعاب‌دار، گل‌هایی که با قلاب بافته شده‌اند، نقره، و چند هدیهٔ کوچک. هر قطعه را جدا انتخاب کرده‌ایم و جدا عکس گرفته‌ایم، در همان گوشهٔ آفتاب‌گیری که در همهٔ عکس‌ها می‌بینید.</p>
</div>
</header>
<section class="wrap block" id="order" aria-labelledby="h-order">
<div class="block-head"><h2 id="h-order">{hl("سفارش، در سه قدم")}</h2><p>سبد خرید نداریم؛ هر قطعه را با کدش سفارش می‌دهید.</p></div>
{order_steps()}
{channel_buttons()}
</section>
<section class="wrap block" id="contact" aria-labelledby="h-contact">
<div class="block-head"><h2 id="h-contact">{hl("تماس")}</h2></div>
{"<ul class='contact-list'>" + contact_items + "</ul>" if contact_items else "<p class='hint'>راه‌های تماس به‌زودی اینجا می‌آید.</p>"}
</section>
"""
    return page("/about/", f'درباره و سفارش — {SITE["name_fa"]}',
                "چطور از " + SITE["name_fa"] + " سفارش بدهیم: کد قطعه را بفرستید.", body,
                crumbs=[("/", "خانه"), ("/about/", "درباره")])


def not_found():
    body = f"""
<header class="sec-head sec-404">
{light("head")}
<div class="wrap">
<p class="eyebrow">۴۰۴</p>
<h1>{hl("این قفسه خالی است")}</h1>
<p class="sec-intro">صفحه‌ای که دنبالش بودید اینجا نیست؛ شاید قطعه‌اش فروخته شده. از مجموعه‌ها شروع کنید:</p>
<ul class="chips-plain">{"".join(f'<li><a class="btn" href="/{c["slug"]}/">{c["fa"]}</a></li>' for c in CAT.CATEGORIES)}</ul>
</div>
</header>"""
    return page("/404.html", f'پیدا نشد — {SITE["name_fa"]}', "این صفحه پیدا نشد.", body)


# ------------------------------------------------------------------ write

def write(path, text):
    full = os.path.join(PUBLIC, path.lstrip("/"))
    if path.endswith("/"):
        full = os.path.join(full, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if full.endswith(".html"):
        text = rebase(text)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def check_picks(by_code):
    bad = [c for c in HOME["hero"] + HOME["shelf"] + list(COVERS.values())
           if c not in by_code or by_code[c]["sold"]]
    if bad:
        raise SystemExit(f"site_config picks that are missing or sold: {bad} — choose others")


TODAY = datetime.date.today()
CSS_URL = JS_URL = None


def main():
    global CSS_URL, JS_URL
    products, by_code = load()
    check_picks(by_code)

    # pages are regenerated wholesale; images and fonts are left where they are
    for entry in os.listdir(PUBLIC) if os.path.isdir(PUBLIC) else []:
        if entry == "assets":
            continue
        full = os.path.join(PUBLIC, entry)
        shutil.rmtree(full) if os.path.isdir(full) else os.remove(full)
    os.makedirs(os.path.join(PUBLIC, "assets"), exist_ok=True)
    for name in ("site.css", "site.js"):
        shutil.copyfile(os.path.join(ASSETS, name), os.path.join(PUBLIC, "assets", name))
    for name in ("favicon.svg", "apple-touch-icon.png"):
        shutil.copyfile(os.path.join(ASSETS, name), os.path.join(PUBLIC, name))
    CSS_URL, JS_URL = asset_url("site.css"), asset_url("site.js")
    with open(os.path.join(HERE, "templates", "htaccess.tpl"), encoding="utf-8") as f:
        htaccess = f.read().replace("__BASE__", BASE).replace("__NAME__", SITE["name_en"])
    write("/.htaccess", htaccess)

    write("/", home(products, by_code))
    for c in CAT.CATEGORIES:
        write(f'/{c["slug"]}/', section_page(c, products))
    pages = 0
    for p in products:
        if not p["sold"]:
            write(p["url"], product_page(p, products))
            pages += 1
    write("/about/", about_page())
    write("/404.html", not_found())

    robots = "User-agent: *\nAllow: /\n"
    if SITE["url"]:
        urls = ["/", "/about/"] + [f'/{c["slug"]}/' for c in CAT.CATEGORIES] + \
               [p["url"] for p in products if not p["sold"]]
        sm = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        sm += [f"<url><loc>{abs_url(u)}</loc></url>" for u in urls]
        sm.append("</urlset>")
        write("/sitemap.xml", "\n".join(sm) + "\n")
        robots += f"Sitemap: {abs_url('/sitemap.xml')}\n"
    write("/robots.txt", robots)
    print(f"built {pages} product pages, {len(CAT.CATEGORIES)} sections, home, about, 404 -> public/")


if __name__ == "__main__":
    sys.exit(main())
