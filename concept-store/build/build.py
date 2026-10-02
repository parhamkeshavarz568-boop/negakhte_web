#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Write the whole site into public/ from the catalogue.

    python build/build.py

Reads  build/data/products.source.json   the catalogue (edit this)
       build/data/images.json            written by make_images.py
       build/site_config.py              name, contacts, home-page picks, banners
Writes public/  — every page, sitemap, robots, 404, .htaccess. Never edit
public/ by hand; the next build overwrites it.

URL map
    /                          home: the sunlit corner, the vitrine, the shelf
    /<section>/                eight sections, e.g. /ceramics/
    /<section>/<code>/         one page per piece that is for sale, e.g. /ceramics/s-10/
    /about/                    about, how to order, contact
    /404.html
"""
import datetime, hashlib, html, json, os, re, shutil, sys, urllib.parse

import catalog as CAT
from site_config import SITE, CONTACT, HOME, COVERS, BANNERS, HANDMADE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBLIC = os.path.join(ROOT, "public")
ASSETS = os.path.join(HERE, "assets")

# The deploy folder: "" when public/ is the web root, "/shop" for a subfolder.
BASE = "/" + (SITE.get("base") or "/").strip("/")
BASE = "" if BASE == "/" else BASE

esc = html.escape


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
    return products, {p["code"]: p for p in products}, images["_atmos"]


def jalali_year(d):
    # The Persian year turns at Nowruz, 20 or 21 March.
    return d.year - 621 if (d.month, d.day) >= (3, 21) else d.year - 622


def fa(n):
    return CAT.fa_digits(n)


# ------------------------------------------------------------------ fragments

def asset_url(name):
    with open(os.path.join(PUBLIC, "assets", name), "rb") as f:
        return f"/assets/{name}?v={hashlib.sha256(f.read()).hexdigest()[:10]}"


def stem(p):
    return p["photo"].split("/")[1][:8]


def picture(p, kind, sizes, eager=False, cls=""):
    """A product photo: <picture> with AVIF + WebP srcsets and its true pixel size."""
    s, im = stem(p), p["img"]
    if kind == "card":
        cands = [(f"/assets/img/{s}-c{w}", w) for w, _ in im["card"]]
        w, h = im["card"][1] if len(im["card"]) > 1 else im["card"][0]
    else:
        w, h = im["full"]
        cands = [(f"/assets/img/{s}-f{w}", w)]
    fallback = f"/assets/img/{s}-{'c' if kind == 'card' else 'f'}{w}.webp"
    avif = ", ".join(f"{u}.avif {cw}w" for u, cw in cands)
    webp = ", ".join(f"{u}.webp {cw}w" for u, cw in cands)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    alt = esc(p["name"] or CAT.CATEGORY[p["category"]]["fa"])
    return (f'<picture class="{cls}"><source type="image/avif" srcset="{avif}" sizes="{sizes}">'
            f'<img src="{fallback}" srcset="{webp}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{alt}" {load} decoding="async"></picture>')


def mood(name, sizes, cls="", eager=False, phone=None):
    """A mood image (build/original/atmosphere/): decorative, so alt="" — it shows
    the shop's light and materials, never a piece for sale. `phone` swaps in a
    tall image below 700px."""
    def sets(n):
        ws = ATMOS[n]["widths"]
        return (", ".join(f"/assets/img/atmos-{n}-{w}.avif {w}w" for w in ws),
                ", ".join(f"/assets/img/atmos-{n}-{w}.webp {w}w" for w in ws))
    W, H = ATMOS[name]["size"]
    a, w_ = sets(name)
    out = [f'<picture class="deco {cls}">']
    if phone:
        pa, pw = sets(phone)
        out.append(f'<source media="(max-width: 699px)" type="image/avif" srcset="{pa}" sizes="100vw">')
        out.append(f'<source media="(max-width: 699px)" type="image/webp" srcset="{pw}" sizes="100vw">')
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    out.append(f'<source type="image/avif" srcset="{a}" sizes="{sizes}">')
    out.append(f'<img src="/assets/img/atmos-{name}-{ATMOS[name]["widths"][-1]}.webp" srcset="{w_}" sizes="{sizes}" '
               f'width="{W}" height="{H}" alt="" {load} decoding="async"></picture>')
    return "".join(out)


def price_html(p, long=False):
    if p["status"] == "available":
        return f'<span class="pr">{CAT.toman(p["price_toman"])} <small>تومان</small></span>'
    if p["status"] == "day":
        return f'<span class="pr pr-ask">{"قیمت به نرخ روز نقره" if long else "قیمت روز"}</span>'
    if p["status"] == "ask":
        return '<span class="pr pr-ask">قیمت را بپرسید</span>'
    return '<span class="pr pr-sold">فروخته شد</span>'


GRID = "(min-width: 1100px) 22vw, (min-width: 700px) 31vw, 46vw"


def item(p, big=False, sizes=GRID):
    """A product card: photo, then code, name and price on one baseline."""
    img = picture(p, "card", sizes, cls="ph")
    if p["sold"]:
        nm = esc(p["name"]) if p["name"] else "&nbsp;"
        return f'<li class="item is-sold">{img}<span class="meta"><span class="nm">{nm}</span>{price_html(p)}</span></li>'
    return (f'<li class="item{" big" if big else ""}"><a href="{p["url"]}">{img}<span class="meta">'
            f'<span class="code">{p["code"]}</span><span class="nm">{esc(p["name"])}</span>{price_html(p)}</span></a></li>')


def channels():
    """[(key, label, href)] for every channel the shop has set. Order = preference."""
    c, out = CONTACT, []
    if c["instagram"]:
        out.append(("instagram", "سفارش در دایرکت اینستاگرام", f"https://ig.me/m/{c['instagram']}"))
    if c["telegram"]:
        out.append(("telegram", "سفارش در تلگرام", f"https://t.me/{c['telegram']}"))
    if c["whatsapp"]:
        out.append(("whatsapp", "سفارش در واتساپ", f"https://wa.me/{c['whatsapp']}"))
    if c["phone"]:
        out.append(("phone", "تماس تلفنی", f"tel:{c['phone']}"))
    return out


def channel_buttons(message=None):
    chs = channels()
    if not chs:
        # Nothing configured yet: the buttons are drawn so the page can be reviewed,
        # but they go nowhere. validate.py lists it as a launch blocker until filled.
        chs = [("instagram", "سفارش در دایرکت اینستاگرام", None), ("phone", "تماس تلفنی", None)]
    out = []
    for i, (key, label, href) in enumerate(chs):
        cls = "btn btn-pri" if i == 0 else "btn"
        if href and key == "whatsapp" and message:
            href += "?text=" + urllib.parse.quote(message)
        if href:
            ext = "" if key == "phone" else ' rel="noopener" target="_blank"'
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
    """negakhte's highlighter: a thin gold bar under the words."""
    return f'<span class="hl">{text}</span>'


def wordmark(cls="wordmark"):
    return f'<a class="{cls}" href="/">{esc(SITE["name_fa"])}<span class="dia" aria-hidden="true"></span></a>'


def for_sale(ps):
    return [p for p in ps if not p["sold"]]


def nums(pairs):
    return '<dl class="nums">' + "".join(f"<div><dt>{t}</dt><dd>{fa(n)}</dd></div>" for t, n in pairs) + "</dl>"


# ------------------------------------------------------------------ shell

NAV = [("/#collections", "ویترین"), ("/about/#order", "سفارش"), ("/about/", "درباره")]


def page(path, title, desc, body, *, og=None, jsonld=None, body_class="", crumbs=None, show_crumbs=True):
    url = abs_url(path)
    og_path, og_w, og_h = og if og else (None, 0, 0)
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        '<meta name="theme-color" content="#F5EFE6">',
        '<meta name="color-scheme" content="light">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="preload" href="/assets/fonts/estedad-subset.woff2" as="font" type="font/woff2" crossorigin>',
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
        if og_path:
            head.append(f'<meta property="og:image" content="{abs_url(og_path)}">')
            head.append(f'<meta property="og:image:width" content="{og_w}">')
            head.append(f'<meta property="og:image:height" content="{og_h}">')
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
    menu = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV)
    menu += "".join(f'<li><a href="/{c["slug"]}/">{c["fa"]}</a></li>' for c in CAT.CATEGORIES)
    crumb_html = ""
    if crumbs and show_crumbs:
        crumb_html = '<nav class="crumbs wrap" aria-label="مسیر">' + crumb_links(crumbs) + "</nav>"

    half = (len(CAT.CATEGORIES) + 1) // 2
    col = lambda cs: "".join(f'<li><a href="/{c["slug"]}/">{c["fa"]}</a></li>' for c in cs)
    contact = "".join(f'<li><a href="{esc(h)}">{l}</a></li>' for _, l, h in channels())
    if CONTACT["address"]:
        contact += f'<li>{esc(CONTACT["address"])}</li>'
    if CONTACT["hours"]:
        contact += f'<li>{esc(CONTACT["hours"])}</li>'
    contact += '<li><a href="/about/#order">چطور سفارش بدهم؟</a></li><li><a href="/about/">درباره</a></li>'
    return f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
{chr(10).join(head)}
</head>
<body class="{body_class}">
<a class="skip" href="#main">رفتن به محتوا</a>
<header class="mast">
<div class="wrap mast-in">
{wordmark()}
<nav class="nav" aria-label="اصلی">{nav}</nav>
<details class="menu"><summary aria-label="فهرست"><span></span></summary><ul>{menu}</ul></details>
</div>
</header>
{crumb_html}
<main id="main">
{body}
</main>
<footer class="foot">
<div class="wrap foot-in">
<div><h2>{esc(SITE["name_fa"])}</h2><p>{esc(SITE["tagline"])}. هر قطعه یک کد دارد؛ کدش را برای ما بفرستید.</p></div>
<div class="foot-cols">
<div><h2>مجموعه‌ها</h2><ul>{col(CAT.CATEGORIES[:half])}</ul></div>
<div><h2>&nbsp;</h2><ul>{col(CAT.CATEGORIES[half:])}</ul></div>
<div><h2>سفارش</h2><ul>{contact}</ul></div>
</div>
</div>
<div class="wrap"><p class="giant" aria-hidden="true">{esc(SITE["name_fa"])}<span class="dia"></span></p>
<p class="foot-small">© {fa(jalali_year(TODAY))} {esc(SITE["name_fa"])}</p></div>
</footer>
<script src="{JS_URL}" defer></script>
</body>
</html>
"""


def crumb_links(crumbs):
    parts = [f'<a href="{u}">{esc(n)}</a>' for u, n in crumbs[:-1]]
    parts.append(f'<span aria-current="page">{esc(crumbs[-1][1])}</span>')
    return '<span aria-hidden="true">/</span>'.join(parts)


# ------------------------------------------------------------------ pages

def order_block(heading_id="h-order"):
    """Three steps, beside the message a customer actually sends."""
    return f"""<section class="wrap order" id="order" aria-labelledby="{heading_id}">
<div>
<p class="eyebrow">بدون سبد خرید</p>
<h2 id="{heading_id}">سفارش، در سه قدم</h2>
<ol class="steps">
<li><span class="step-n">۱</span><div><h3>قطعه را انتخاب کنید</h3><p>هر قطعه یک کد دارد، مثل <span class="code">S-10</span>، کنار نامش.</p></div></li>
<li><span class="step-n">۲</span><div><h3>کد را بفرستید</h3><p>در دایرکت یا پیام؛ موجودی را همان لحظه می‌گوییم.</p></div></li>
<li><span class="step-n">۳</span><div><h3>هماهنگی ارسال</h3><p>پرداخت و ارسال یا تحویل را با هم هماهنگ می‌کنیم.</p></div></li>
</ol>
{channel_buttons()}
</div>
<figure class="chat" aria-label="نمونهٔ پیام سفارش">
<figcaption class="chat-who"><i></i>نمونهٔ پیام شما به فروشگاه</figcaption>
<p class="bubble">سلام! این قطعه را می‌خواهم:<br><span class="code">S-10</span> — ماگ لعابی جنگلی</p>
<p class="chat-note">دکمهٔ «کپی کد و نام» در صفحهٔ هر قطعه همین پیام را آماده می‌کند.</p>
</figure>
</section>"""


VIT_SIZES = "(hover: hover) and (min-width: 900px) 31vw, (min-width: 700px) 42vw, 76vw"


def home(products, by_code):
    total = len(for_sale(products))
    sold = len(products) - total
    panes = []
    for i, c in enumerate(CAT.CATEGORIES):
        cover = by_code[COVERS[c["slug"]]]
        n = len(for_sale([p for p in products if p["category"] == c["slug"]]))
        panes.append(f'<li class="pane{" is-open" if i == 0 else ""}"><a href="/{c["slug"]}/">'
                     f'{picture(cover, "card", VIT_SIZES)}'
                     f'<span class="tag"><b>{c["fa"]}</b><em>{fa(n)} قطعه</em></span></a></li>')
    shelf = [by_code[c] for c in HOME["shelf"]]
    big = {0, 7}
    shelf_html = "".join(
        item(p, big=i in big, sizes="(min-width: 900px) 46vw, 100vw" if i in big else
             "(min-width: 900px) 22vw, 46vw") for i, p in enumerate(shelf))
    line = esc(SITE["tagline"])
    em = esc(SITE.get("tagline_em") or "")
    first, _, rest = line.partition("، ")
    if em and em in first:
        first = first.replace(em, f'<b class="hl">{em}</b>', 1)
    counts = {s: len(for_sale([p for p in products if p["category"] == s]))
              for s in ("candles", "ceramics", "knitted-flowers")}
    body = f"""
<section class="hero">
{mood("hero-wide", "100vw", cls="hero-bg", eager=True, phone="hero-tall")}
<canvas class="motes" aria-hidden="true"></canvas>
<div class="wrap hero-in">
<div class="hero-copy">
<p class="eyebrow">دست‌ساز و انتخابی</p>
<h1 class="hero-h1"><span class="ln">{first}،</span> <span class="ln">{rest}</span></h1>
<p class="hero-lede">شمع، سفال، گل بافتنی، نقره و هدیه‌های کوچک. هر قطعه یک کد دارد؛ کدش را برای ما بفرستید.</p>
<div class="hero-cta"><a class="btn btn-pri" href="#collections">دیدن ویترین</a><a class="btn" href="#order">چطور سفارش بدهم؟</a></div>
</div>
<dl class="hero-stats"><div><dt>قطعه برای فروش</dt><dd>{fa(total)}</dd></div><div><dt>مجموعه</dt><dd>{fa(len(CAT.CATEGORIES))}</dd></div><div><dt>به خانهٔ تازه رفته</dt><dd>{fa(sold)}</dd></div></dl>
</div>
</section>

<section class="vitrine" id="collections" aria-labelledby="h-collections">
<div class="wrap sec-head"><div><p class="eyebrow">ویترین</p><h2 id="h-collections">هشت مجموعه</h2></div>
<p class="sec-aside">از شمع و سفال تا گل بافتنی، نقره، عود و ادویه.</p></div>
<ul class="vit">{"".join(panes)}</ul>
</section>

<section class="wrap shelf" aria-labelledby="h-shelf">
<div class="sec-head"><div><p class="eyebrow">از قفسه‌ها</p><h2 id="h-shelf">تازه در ویترین</h2></div>
<a class="sec-link" href="#collections">همهٔ {fa(total)} قطعه، در هشت مجموعه ←</a></div>
<ul class="ed">{shelf_html}</ul>
</section>

<section class="state" aria-labelledby="h-state">
{mood("light-ledge", "(min-width: 900px) 50vw, 100vw", cls="state-ph")}
<div class="state-tx">
<p class="eyebrow">دست‌ساز</p>
<h2 id="h-state">با دست،<br><b>یکی‌یکی.</b></h2>
<p>شمع‌های آیشید، سفالِ لعاب‌دار و گل‌هایی که دانه‌به‌دانه با قلاب بافته شده‌اند. بیشترشان یک بار ساخته می‌شوند؛ وقتی رفتند، رفته‌اند.</p>
{nums([("شمع", counts["candles"]), ("سفال", counts["ceramics"]), ("گل بافتنی", counts["knitted-flowers"])])}
</div>
</section>

{order_block()}
"""
    store = {"@context": "https://schema.org", "@type": "Store", "name": SITE["name_fa"],
             "description": SITE["description"], "url": abs_url("/"), "image": abs_url("/assets/img/og-home.jpg")}
    if CONTACT["phone"]:
        store["telephone"] = CONTACT["phone"]
    if CONTACT["address"]:
        store["address"] = {"@type": "PostalAddress", "streetAddress": CONTACT["address"],
                            "addressLocality": CONTACT["city"] or "", "addressCountry": "IR"}
    return page("/", f'{SITE["name_fa"]} — {SITE["tagline"]}', SITE["description"], body,
                og=("/assets/img/og-home.jpg", 1200, 630), jsonld=store, body_class="is-home")


def sec_hero(eyebrow, title_html, intro, banner, extra="", long=False):
    return f"""<header class="sec-hero">
<div class="wrap sec-hero-in">
<div class="sec-copy"><p class="eyebrow">{eyebrow}</p><h1{' class="long"' if long else ""}>{title_html}</h1>
<p class="sec-intro">{intro}</p>{extra}</div>
{mood(banner, "(min-width: 900px) 55vw, 100vw", cls="sec-ph", eager=True)}
</div>
</header>"""


def section_page(c, products):
    ps = [p for p in products if p["category"] == c["slug"]]
    live, sold = for_sale(ps), [p for p in ps if p["sold"]]
    tabs = "".join(f'<li><a href="/{o["slug"]}/"{" aria-current=\"page\"" if o is c else ""}>{o["fa"]}</a></li>'
                   for o in CAT.CATEGORIES)
    counts = [("برای فروش", len(live))] + ([("فروخته‌شده", len(sold))] if sold else [])
    sold_html = ""
    if sold:
        sold_html = f"""
<section class="wrap sold" aria-labelledby="h-sold">
<h2 id="h-sold">به خانهٔ {hl("تازه")} رفتند</h2>
<p class="sec-aside">{fa(len(sold))} قطعه از این قفسه فروخته شده. اگر مشابهش را می‌خواهید، بپرسید.</p>
<ul class="grid-sold">{"".join(item(p, sizes="(min-width: 700px) 15vw, 30vw") for p in sold)}</ul>
</section>"""
    body = f"""
{sec_hero("مجموعه", f'{c["fa"]}<b>.</b>', esc(c["intro"]), BANNERS[c["slug"]], nums(counts))}
<nav class="tabs" aria-label="مجموعه‌ها"><div class="wrap"><ul>{tabs}</ul></div></nav>
<section class="wrap listing" aria-label="{c["fa"]} — برای فروش">
<ul class="grid">{"".join(item(p) for p in live)}</ul>
</section>
{sold_html}
"""
    cover = live[0] if live else ps[0]
    return page(f'/{c["slug"]}/', f'{c["fa"]} — {SITE["name_fa"]}',
                f'{c["intro"]} {fa(len(live))} قطعه برای فروش.', body,
                og=(f"/assets/img/{stem(cover)}-og.jpg", 480, 600) if cover["img"]["og"] else None,
                crumbs=[("/", "خانه"), (f'/{c["slug"]}/', c["fa"])], body_class="is-section")


BRANDS = (("نیکس‌ژل", "Nixgel"), ("نیورا", "Niura"), ("الورا", "ELORA"))


def product_page(p, products):
    c = CAT.CATEGORY[p["category"]]
    same = for_sale([q for q in products if q["category"] == p["category"]])
    i = same.index(p)
    related = (same[i + 1:] + same[:i])[:4]
    message = f"سلام! این قطعه را می‌خواهم:\n{p['code']} — {p['name']}"
    if SITE["url"]:
        message += "\n" + abs_url(p["url"])
    notes = []
    if p["category"] in HANDMADE:
        notes.append("دست‌ساز است و هر قطعه فقط یکی؛ ممکن است با عکس کمی تفاوت داشته باشد.")
    if p["status"] == "day":
        notes.append("قیمت نقره هر روز تغییر می‌کند؛ قیمتِ امروز را در پیام می‌گوییم.")
    notes.append("کد را بفرستید؛ موجودی، پرداخت و ارسال را همان‌جا هماهنگ می‌کنیم.")
    crumbs = [("/", "خانه"), (f'/{c["slug"]}/', c["fa"]), (p["url"], p["name"])]
    rel_html = ""
    if related:
        rel_html = f"""
<section class="wrap more" aria-labelledby="h-more">
<div class="sec-head"><div><p class="eyebrow">از همین قفسه</p><h2 id="h-more">باز هم {c["fa"]}</h2></div>
<a class="sec-link" href="/{c["slug"]}/">همهٔ {fa(len(same))} قطعه ←</a></div>
<ul class="grid">{"".join(item(q) for q in related)}</ul>
</section>"""
    body = f"""
<article class="prod">
<div class="prod-ph">{picture(p, "full", "(min-width: 900px) 56vw, 100vw", eager=True)}</div>
<div class="prod-info">
<nav class="crumbs" aria-label="مسیر">{crumb_links(crumbs)}</nav>
<p class="eyebrow"><a href="/{c["slug"]}/">{c["fa"]}</a></p>
<h1>{esc(p["name"])}</h1>
<p class="prod-price">{price_html(p, long=True)}</p>
<div class="codebox" id="order"><span>کد قطعه</span><span class="code">{p["code"]}</span>
<button class="copy" type="button" data-copy="{esc(message)}">کپی کد و نام</button></div>
{channel_buttons(message)}
<ul class="notes">{"".join(f"<li>{n}</li>" for n in notes)}</ul>
<button class="share" type="button" hidden data-share-title="{esc(p["name"])}">فرستادن برای یک دوست</button>
</div>
</article>
<div class="buybar" aria-hidden="true"><div class="wrap buybar-in">{price_html(p)}<a class="btn btn-pri" href="#order" tabindex="-1">سفارش با کد <span class="code">{p["code"]}</span></a></div></div>
{rel_html}
"""
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "sku": p["code"],
          "image": abs_url(f"/assets/img/{stem(p)}-f{p['img']['full'][0]}.webp"),
          "url": abs_url(p["url"]), "category": c["fa"]}
    for fa_, en in BRANDS:
        if fa_ in p["name"]:
            ld["brand"] = {"@type": "Brand", "name": en}
    if p["status"] == "available":
        # Schema.org wants ISO 4217 and Toman has no code: publish the Rial value.
        ld["offers"] = {"@type": "Offer", "price": p["price_toman"] * 10, "priceCurrency": "IRR",
                        "availability": "https://schema.org/InStock", "url": abs_url(p["url"])}
    desc = f'{p["name"]} — {c["fa"]}، کد {p["code"]}. '
    desc += (f'{CAT.toman(p["price_toman"])} تومان.' if p["status"] == "available" else "قیمت را بپرسید.")
    return page(p["url"], f'{p["name"]} · {p["code"]} — {SITE["name_fa"]}', desc, body,
                og=(f"/assets/img/{stem(p)}-og.jpg", 480, 600), jsonld=ld, body_class="is-product",
                crumbs=crumbs, show_crumbs=False)


def about_page():
    items = "".join(f'<li><a href="{esc(h)}">{l}</a></li>' for _, l, h in channels())
    if CONTACT["phone_display"]:
        items += f'<li>تلفن: <span class="code">{esc(CONTACT["phone_display"])}</span></li>'
    if CONTACT["address"]:
        items += f'<li>نشانی: {esc(CONTACT["address"])}</li>'
    if CONTACT["hours"]:
        items += f'<li>ساعت کار: {esc(CONTACT["hours"])}</li>'
    intro = ("یک فروشگاه کوچک برای چیزهایی که دوست داریم: شمع‌های دست‌ساز، سفالِ لعاب‌دار، "
             "گل‌هایی که با قلاب بافته شده‌اند، نقره، و چند هدیهٔ کوچک. هر قطعه را جدا انتخاب "
             "کرده‌ایم و جدا عکس گرفته‌ایم، در نور آفتابِ عصر.")
    contact = (f"<ul class='contact-list'>{items}</ul>" if items
               else "<p class='sec-aside'>راه‌های تماس به‌زودی اینجا می‌آید.</p>")
    body = f"""
{sec_hero("درباره", f'{esc(SITE["name_fa"])}<b>.</b>', intro, "light-ledge", long=True)}
{order_block()}
<section class="wrap" id="contact" aria-labelledby="h-contact">
<div class="sec-head"><div><p class="eyebrow">تماس</p><h2 id="h-contact">با ما در تماس باشید</h2></div></div>
{contact}
</section>
"""
    return page("/about/", f'درباره و سفارش — {SITE["name_fa"]}',
                "چطور از " + SITE["name_fa"] + " سفارش بدهیم: کد قطعه را بفرستید.", body,
                crumbs=[("/", "خانه"), ("/about/", "درباره")])


def not_found():
    chips = "".join(f'<a class="btn" href="/{c["slug"]}/">{c["fa"]}</a>' for c in CAT.CATEGORIES)
    body = sec_hero("۴۰۴", 'این قفسه خالی است<b>.</b>',
                    "صفحه‌ای که دنبالش بودید اینجا نیست؛ شاید قطعه‌اش فروخته شده. از مجموعه‌ها شروع کنید:",
                    "hero-tall", f'<div class="chips">{chips}</div>', long=True)
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
    bad = [c for c in HOME["shelf"] + list(COVERS.values()) if c not in by_code or by_code[c]["sold"]]
    if bad:
        raise SystemExit(f"site_config picks that are missing or sold: {bad} — choose others")
    missing = [b for b in set(BANNERS.values()) if b not in ATMOS]
    if missing:
        raise SystemExit(f"site_config BANNERS name mood images that do not exist: {missing}")


TODAY = datetime.date.today()
CSS_URL = JS_URL = None
ATMOS = {}


def main():
    global CSS_URL, JS_URL, ATMOS
    products, by_code, ATMOS = load()
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
        write("/.htaccess", f.read().replace("__BASE__", BASE).replace("__NAME__", SITE["name_en"]))

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
