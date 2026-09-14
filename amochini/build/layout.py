# -*- coding: utf-8 -*-
"""Shared chrome: <head>, header, nav, footer, and the SEO/JSON-LD helpers."""
import json, html, os as _os
from normalize import to_fa_digits, BRANDS, CATEGORIES
from site_config import SITE, CONTACT, SOCIAL, COMMERCE, TRUST, ANALYTICS, SUPPLIER

BASE = SITE["base_url"]


def e(s):
    """Escape for HTML text/attribute context."""
    return html.escape(str(s if s is not None else ""), quote=True)


def ld(obj):
    """Render a JSON-LD block. ensure_ascii=False keeps Persian readable in source;
    2-space indent costs a few bytes and makes debugging structured data sane."""
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>")


# CLDR's thousands separator for fa is U+066C ARABIC THOUSANDS SEPARATOR —
# not U+060C ARABIC COMMA (which is a list separator) and not an ASCII comma.
FA_GROUP = "\u066C"


def money(rial, unit=True, data=False):
    """Rial int -> Persian-digit Toman string, for DISPLAY only.

    Never feed this to JSON-LD: schema.org needs Latin digits and the raw
    Rial integer. `data=True` wraps the number in <data value="..."> carrying
    the Latin Rial value, so the machine-readable figure is present in the DOM
    at the visible price and there is no ambiguity between the two."""
    if rial is None:
        return None
    t = rial // COMMERCE["display_divisor"]
    txt = to_fa_digits(f"{t:,}").replace(",", FA_GROUP)
    if data:
        txt = f'<data value="{rial}">{txt}</data>'
    return f"{txt} <small>{COMMERCE['display_unit']}</small>" if unit else txt


def bdi(s):
    """Wrap a Latin run so its punctuation doesn't jump ends inside RTL text."""
    return f"<bdi>{e(s)}</bdi>"


# --------------------------------------------------------------- navigation
NAV = [
    ("/", "صفحه اصلی"),
    ("/prices/", "قیمت روز"),
    ("/brake-pads/", "لنت ترمز"),
    ("/brake-discs/", "دیسک چرخ"),
    ("/brake-drums/", "کاسه چرخ"),
    ("/brands/", "خودروها"),
    ("/about/", "درباره ما"),
    ("/contact/", "تماس با ما"),
]

SVG = dict(
    phone='<path d="M5 3h4l2 5-2.5 1.5a12 12 0 006 6L16 13l5 2v4a2 2 0 01-2.2 2A17 17 0 013 5.2 2 2 0 015 3z"/>',
    search='<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    user='<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    pin='<path d="M12 21s7-6.3 7-11a7 7 0 10-14 0c0 4.7 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    mail='<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    clock='<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
)

SOCIAL_ICONS = dict(
    instagram=('ig', 'اینستاگرام', 'https://instagram.com/{}',
               '<path d="M12 2.2c3.2 0 3.6 0 4.9.07 1.2.05 1.8.25 2.2.42.6.22 1 .48 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c0 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2 0-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c0-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 3.2A6.6 6.6 0 1018.6 12 6.6 6.6 0 0012 5.4zm0 10.9A4.3 4.3 0 1116.3 12 4.3 4.3 0 0112 16.3zm6.9-11.1a1.55 1.55 0 11-1.55-1.55A1.55 1.55 0 0118.9 5.2z"/>'),
    telegram=('tg', 'تلگرام', 'https://t.me/{}',
              '<path d="M21.9 4.3l-3 14.2c-.2 1-.8 1.3-1.7.8l-4.6-3.4-2.2 2.1c-.25.25-.45.45-.9.45l.33-4.7L18.4 5.5c.37-.33-.08-.5-.57-.18L6.2 12.6l-4.6-1.4c-1-.3-1-1 .2-1.5L20.6 2.5c.83-.3 1.55.2 1.3 1.8z"/>'),
    whatsapp=('wa', 'واتساپ', 'https://wa.me/{}',
              '<path d="M17.5 14.4c-.3-.15-1.75-.86-2-.96-.27-.1-.47-.15-.66.15s-.76.96-.93 1.16-.35.22-.64.07a8.1 8.1 0 01-2.4-1.48 9 9 0 01-1.66-2.06c-.17-.3 0-.46.13-.6l.45-.52a2 2 0 00.3-.5.55.55 0 000-.52c-.07-.15-.66-1.6-.9-2.18s-.48-.5-.66-.51h-.57a1.1 1.1 0 00-.8.37 3.3 3.3 0 00-1.03 2.46 5.75 5.75 0 001.2 3.04 13.1 13.1 0 005.02 4.44 16.9 16.9 0 001.68.62 4 4 0 001.85.12 3 3 0 002-1.4 2.45 2.45 0 00.17-1.4c-.07-.13-.27-.2-.56-.34zM12 2a10 10 0 00-8.6 15.1L2 22l5-1.3A10 10 0 1012 2zm0 18.2a8.2 8.2 0 01-4.2-1.15l-.3-.18-3.1.8.83-3-.2-.31A8.2 8.2 0 1112 20.2z"/>'),
    eitaa=('ea', 'ایتا', 'https://eitaa.com/{}',
           '<path d="M12 2a10 10 0 100 20 10 10 0 000-20zm4.6 6.8l-1.6 7.6c-.12.54-.44.67-.9.42l-2.48-1.83-1.2 1.15c-.13.13-.25.25-.5.25l.18-2.53 4.6-4.16c.2-.18-.04-.28-.3-.1l-5.7 3.58-2.45-.77c-.53-.16-.54-.53.11-.79l9.57-3.69c.44-.16.83.1.67.87z"/>'),
)


def social_links():
    out = []
    for key, (cls, label, urlfmt, path) in SOCIAL_ICONS.items():
        handle = SOCIAL.get(key) or (CONTACT["whatsapp"] if key == "whatsapp" else "")
        if not handle:
            continue
        out.append(f'<a class="{cls}" href="{e(urlfmt.format(handle))}" '
                   f'aria-label="{e(label)}" rel="noopener" target="_blank">'
                   f'<svg viewBox="0 0 24 24" aria-hidden="true">{path}</svg></a>')
    return "\n        ".join(out)


def sameas():
    """schema.org sameAs — only real, filled-in profiles."""
    out = []
    for key, (_c, _l, urlfmt, _p) in SOCIAL_ICONS.items():
        h = SOCIAL.get(key)
        if h and key != "whatsapp":
            out.append(urlfmt.format(h))
    return out


# --------------------------------------------------------------- head/foot
def head(*, title, description, canonical, jsonld=(), og_image=None,
         og_type="website", robots=None, extra=""):
    """Build the <head>. `canonical` is a site-root-relative path like /about/."""
    url = BASE + canonical
    img = og_image or "/assets/img/hero-bg-1024.jpg"
    parts = [
        '<!DOCTYPE html>',
        f'<html lang="{SITE["lang"]}" dir="rtl">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{e(title)}</title>',
        f'<meta name="description" content="{e(description)}">',
        f'<link rel="canonical" href="{e(url)}">',
    ]
    # A preview build is noindexed at the source. It replaces the visible
    # banner: no clutter while reviewing the design, but a copy that leaks
    # onto a server still cannot enter the index.
    if _os.environ.get("PREVIEW_NOINDEX"):
        robots = "noindex, nofollow"
    if robots:
        parts.append(f'<meta name="robots" content="{e(robots)}">')
    parts += [
        f'<meta name="theme-color" content="{SITE["theme_color"]}">',
        # --- Open Graph / Twitter ---
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{e(SITE["name_fa"])}">',
        f'<meta property="og:locale" content="{SITE["locale"]}">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(description)}">',
        f'<meta property="og:url" content="{e(url)}">',
        f'<meta property="og:image" content="{e(BASE + img)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e(title)}">',
        f'<meta name="twitter:description" content="{e(description)}">',
        f'<meta name="twitter:image" content="{e(BASE + img)}">',
        # --- icons ---
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        '<link rel="alternate icon" href="/favicon.ico" sizes="32x32">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="manifest" href="/site.webmanifest">',
        # --- font: self-hosted, preloaded, no third-party origin ---
        '<link rel="preload" href="/assets/fonts/vazirmatn-subset.woff2" as="font" '
        'type="font/woff2" crossorigin>',
        '<link rel="stylesheet" href="/assets/css/site.css">',
    ]
    # No hero <link rel=preload>: the hero is negotiated across AVIF/WebP/JPEG
    # by <picture>, and a preload can only name one format — naming the wrong
    # one buys a wasted download. fetchpriority="high" on the <img> is the
    # correct signal and it respects the negotiation.
    for block in jsonld:
        parts.append(ld(block))
    if ANALYTICS["head_html"]:
        parts.append(ANALYTICS["head_html"])
    if extra:
        parts.append(extra)
    parts.append("</head>")
    return "\n".join(parts)


def header(active="/"):
    CUR = ' aria-current="page"'
    nav = "\n      ".join(
        f'<a href="{e(u)}"{CUR if u == active else ""}>{e(t)}</a>'
        for u, t in NAV)
    return f'''<body>
<a class="skip" href="#main">پرش به محتوای اصلی</a>

<div class="topbar">
  <div class="wrap">
    <nav aria-label="لینک‌های کمکی">
      <a href="/contact/">تماس با ما</a>
      <a href="/about/">درباره ما</a>
      <a href="/brands/">راهنمای خودروها</a>
    </nav>
    <span class="asmco-badge">{e(SUPPLIER["claim_fa"])}</span>
    <div class="account">
      <span class="tb-hours"><svg viewBox="0 0 24 24" aria-hidden="true">{SVG["clock"]}</svg>
        {e(CONTACT["hours_display"])}</span>
      <span class="tb-phone"><svg viewBox="0 0 24 24" aria-hidden="true">{SVG["phone"]}</svg>
        سفارش تلفنی: <a href="tel:{e(CONTACT["phone_tel"])}">{bdi(CONTACT["phone_display"])}</a></span>
    </div>
  </div>
</div>

<header class="masthead">
  <div class="wrap">
    <a href="/" class="logo">عمو<span>چینی</span>
      <small>{e(SITE["slogan"])}</small>
    </a>

    <form class="search" role="search" action="/brake-pads/" method="get" id="siteSearch">
      <label class="sr-only" for="q-top">جستجوی محصول</label>
      <button type="submit" aria-label="جستجو">
        <svg viewBox="0 0 24 24" aria-hidden="true">{SVG["search"]}</svg>
      </button>
      <input type="search" id="q-top" name="q" autocomplete="off"
             placeholder="جستجو با نام قطعه، خودرو یا کد کالا"
             aria-describedby="q-help">
      <div class="suggest" id="suggest" role="listbox" aria-label="پیشنهادها"></div>
    </form>
    <p class="sr-only" id="q-help">برای مثال: لنت ترمز ام‌وی‌ام ۳۱۵ جلو</p>

  </div>
</header>

<div class="menubar">
  <div class="wrap">
    <button class="menu-toggle" aria-expanded="false" aria-controls="mainnav">
      <span class="bars" aria-hidden="true"><i></i><i></i><i></i></span> منو
    </button>
    <nav id="mainnav" aria-label="منوی اصلی">
      {nav}
    </nav>
  </div>
</div>
'''


def crumbs(items):
    """items: [(url|None, label)]. Last item is the current page."""
    lis = []
    for u, label in items:
        if u:
            lis.append(f'<li><a href="{e(u)}">{e(label)}</a></li>')
        else:
            lis.append(f'<li><span aria-current="page">{e(label)}</span></li>')
    return ('<nav class="crumbs wrap" aria-label="مسیر صفحه"><ol>'
            + "".join(lis) + "</ol></nav>")


def crumbs_ld(items):
    """BreadcrumbList matching what crumbs() rendered."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label,
             **({"item": BASE + u} if u else {})}
            for i, (u, label) in enumerate(items)
        ],
    }


def trust_slots():
    rows = []
    if TRUST["enamad_code"]:
        rows.append(TRUST["enamad_code"])
    else:
        rows.append('<div class="slot">جای نماد<br>اعتماد الکترونیکی</div>')
    if TRUST["samandehi_code"]:
        rows.append(TRUST["samandehi_code"])
    else:
        rows.append('<div class="slot">جای نشان<br>ساماندهی</div>')
    return "\n        ".join(rows)


def footer():
    quick = "".join(f'<li><a href="{e(u)}">{e(t)}</a></li>' for u, t in NAV[1:])
    socials = social_links()
    social_block = (f'<h2>ما را دنبال کنید</h2>\n      <div class="social">{socials}</div>'
                    if socials else
                    '<h2>ما را دنبال کنید</h2>\n      <p style="color:#8f8f8f;font-size:13px">'
                    'به‌زودی</p>')
    return f'''
<section class="features">
  <div class="wrap">
    <ul>
      <li>
        <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M4 12h22v20H4z"/><path d="M26 18h9l6 7v7h-15z"/><circle cx="13" cy="35" r="3.5"/><circle cx="33" cy="35" r="3.5"/></svg>
        <b>ارسال به سراسر کشور</b><small>ارسال رایگان برای خرید بالای {to_fa_digits(f"{COMMERCE['free_shipping_over_toman']:,}").replace(",","،")} تومان</small>
      </li>
      <li>
        <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M40 24a16 16 0 11-5-11.6"/><path d="M38 6v8h-8"/></svg>
        <b>ضمانت بازگشت</b><small>{to_fa_digits(COMMERCE["return_days"])} روز ضمانت بازگشت وجه</small>
      </li>
      <li>
        <svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="18"/><path d="M24 15v10l6 4"/></svg>
        <b>مشاوره فنی</b><small>راهنمایی برای انتخاب قطعه مناسب خودرو</small>
      </li>
      <li>
        <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 6l14 6v10c0 9-6 15-14 20-8-5-14-11-14-20V12z"/><path d="M18 24l5 5 9-10"/></svg>
        <b>قطعات اصلی</b><small>تضمین اصالت کالا</small>
      </li>
    </ul>
  </div>
</section>

<footer>
  <div class="wrap cols">
    <div>
      <div class="f-logo">عمو<span>چینی</span></div>
      <p class="f-claim">{e(SUPPLIER["claim_fa"])}</p>
      <ul class="contact">
        <li>
          <svg viewBox="0 0 24 24" aria-hidden="true">{SVG["pin"]}</svg>
          <b><a href="{e(CONTACT["map_url"])}" rel="noopener" target="_blank">{e(CONTACT["street"])}</a>
          <small>{e(CONTACT["city"])} — مشاهده روی نقشه</small></b>
        </li>
        <li>
          <svg viewBox="0 0 24 24" aria-hidden="true">{SVG["phone"]}</svg>
          <span><b><a href="tel:{e(CONTACT["phone_tel"])}">{bdi(CONTACT["phone_display"])}</a></b>
          <small>{e(CONTACT["hours_display"])}</small></span>
        </li>
        <li>
          <svg viewBox="0 0 24 24" aria-hidden="true">{SVG["mail"]}</svg>
          <b><a href="mailto:{e(CONTACT["email"])}">{bdi(CONTACT["email"])}</a></b>
        </li>
      </ul>
    </div>

    <div>
      {social_block}
      <h2 style="margin-top:34px">دسترسی سریع</h2>
      <ul class="quick">{quick}</ul>
    </div>

    <div>
      <h2>نمادها</h2>
      <div class="trust">
        {trust_slots()}
      </div>
      <h2 style="margin-top:30px">پرداخت</h2>
      <div class="pay"><span>شتاب</span><span>سامان</span><span>ملت</span></div>
    </div>
  </div>

  <div class="copyright">
    © تمامی حقوق برای {e(SITE["name_fa"])} محفوظ است — {e(SITE["domain"])}
  </div>
</footer>

<script src="/assets/js/site.js" defer></script>
{ANALYTICS["body_end_html"]}
</body>
</html>'''
