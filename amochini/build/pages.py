# -*- coding: utf-8 -*-
"""Page bodies. Each function returns a full HTML document."""
from normalize import to_fa_digits, BRANDS, CATEGORIES, VARIANTS, AXLES
from site_config import SITE, CONTACT, COMMERCE, SOCIAL, SUPPLIER
from layout import (latin_bdi, e, ld, money, bdi, head, header, footer, crumbs, crumbs_ld,
                    BASE, sameas, SVG)
import json as _json, os as _os
import prices as PR

# Filled in by build.py once the history is loaded.
PRICE_META = dict(observations=0, tracked=0, skus=0, latest=None,
                  index={}, index_series=[], breadth={}, synthetic=False)


def _synth_note():
    """One sentence, in the board's existing footnote, when the history on
    disk was seeded rather than observed.

    Deliberately a sentence and not a banner — the owner asked for the banner
    to go and he was right, a red bar across every page is not the way to say
    this. But the site's whole argument is that its numbers are dated and
    true, so the one place it shows movement it did not observe has to say so.
    It disappears by itself the moment build/data/SYNTHETIC is removed.
    """
    if not PRICE_META.get("synthetic"):
        return ""
    return (" قیمت امروز هر کالا واقعی است؛ نمودار و درصد تغییر تا تکمیل "
            "ثبت روزانه، نمونه‌ای است.")


def dataset_ld(ix):
    """schema.org Dataset for the published feeds.

    This describes the FEED FILES, which exist and are real. It carries no
    price series of its own: the only price schema.org gets from this site is
    the current Offer on each product page, and that figure is the true
    catalogue price. Nothing here tells a search engine that a price moved.
    """
    d = {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "قیمت روز قطعات ترمز خودروهای چینی",
        "description": ("قیمت روز و سابقه قیمت لنت ترمز، دیسک چرخ و کاسه چرخ "
                        "خودروهای چینی، با تاریخ هر ثبت."),
        "url": BASE + "/prices/",
        "inLanguage": "fa-IR",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "creator": {"@id": BASE + "/#org"},
        "isAccessibleForFree": True,
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "application/json",
             "contentUrl": BASE + "/prices.json"},
            {"@type": "DataDownload", "encodingFormat": "text/csv",
             "contentUrl": BASE + "/prices.csv"},
        ],
    }
    if ix.get("base_date"):
        d["temporalCoverage"] = f"{ix['base_date']}/{PRICE_META['latest']}"
    if PRICE_META.get("synthetic"):
        # Said in the machine-readable layer too, not only to human readers.
        d["disambiguatingDescription"] = (
            "Historical observations are illustrative pending real daily "
            "recording; the most recent price of each product is actual.")
    return d

# Which renditions actually exist on disk, written by build.py from the files
# make_images.py produced. Loaded LAZILY: build.py regenerates the manifest
# during its run, so caching it at import time would pin the previous build's
# version and let a template reference a file that no longer exists.
_IMG_CACHE = {}


def _img_meta():
    if not _IMG_CACHE:
        path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                             "data", "images.json")
        _IMG_CACHE.update(_json.load(open(path, encoding="utf-8")))
    return _IMG_CACHE


def img_w(name, want):
    """Largest available width <= want, else the smallest available."""
    sizes = _img_meta().get(name, {}).get("widths")
    if not sizes:
        return want
    ok = [s for s in sizes if s <= want]
    return max(ok) if ok else min(sizes)


def picture(name, *, alt, box, sizes=None, eager=False, cls=""):
    """A three-format <picture>.

    AVIF -> WebP -> JPEG, in that order: the browser takes the first type it
    supports. WebP is not redundant — it is the layer that serves the older
    Android WebView tail still common in Iran, which AVIF misses.

    `box` is the rendered CSS width of the largest instance, measured in a real
    browser (see docs/MEASUREMENTS.md). Renditions offered are those at or
    below 2x that, so a 108px thumbnail never ships a 400px file.

    `eager` must be True for anything in the first viewport: loading="lazy" on
    an above-the-fold image defers its request until after layout and directly
    delays LCP.
    """
    meta = _img_meta().get(name, {})
    widths = meta.get("widths") or [box]
    formats = meta.get("formats") or ["jpg"]
    use = [w for w in widths if w <= box * 2] or [min(widths)]
    fallback = max(use)
    ar = meta.get("ar", 1.0)
    srcset = lambda ext: ", ".join(
        f"/assets/img/{name}-{w}.{ext} {w}w" for w in use)
    src = []
    for ext, mime in (("avif", "image/avif"), ("webp", "image/webp")):
        if ext in formats:
            src.append(f'<source type="{mime}" srcset="{srcset(ext)}"'
                       + (f' sizes="{sizes}"' if sizes else "") + ">")
    load = ('loading="eager" fetchpriority="high"' if eager
            else 'loading="lazy" decoding="async"')
    return (f'<picture{f" class={cls}" if cls else ""}>'
            + "".join(src)
            + f'<img src="/assets/img/{name}-{fallback}.jpg" alt="{e(alt)}"'
            + (f' srcset="{srcset("jpg")}"' if len(use) > 1 else "")
            + (f' sizes="{sizes}"' if sizes else "")
            + f' width="{fallback}" height="{round(fallback*ar)}" {load}>'
            + "</picture>")

AXLE_FA = {"front": "جلو", "rear": "عقب"}
CAT_ORDER = ["brake-pads", "brake-discs", "brake-drums"]


# ------------------------------------------------------------------ shared
def org_ld():
    """AutoPartsStore is a real schema.org type (Store > AutomotiveBusiness)."""
    node = {
        "@context": "https://schema.org",
        # Multi-typed on purpose: OnlineStore is the Google-supported
        # Organization subtype, AutoPartsStore is the precise vertical.
        "@type": ["OnlineStore", "AutoPartsStore"],
        "@id": BASE + "/#org",
        "name": SITE["name_fa"],
        "alternateName": SITE["name_en"],
        "slogan": SITE["slogan"],
        "url": BASE + "/",
        "description": SITE["description"],
        "logo": {"@type": "ImageObject", "url": BASE + "/icon-512.png",
                 "width": 512, "height": 512},
        "image": BASE + "/assets/img/hero-bg-1024.jpg",
        "telephone": CONTACT["phone_tel"],
        "email": CONTACT["email"],
        "priceRange": "$$",
        "currenciesAccepted": "IRR",
        "paymentAccepted": "نقدی، کارت بانکی (شتاب)",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": CONTACT["street"],
            "addressLocality": CONTACT["city"],
            "addressRegion": CONTACT["region"],
            "addressCountry": CONTACT["country"],
        },
        "openingHours": CONTACT["hours_schema"],
        "areaServed": {"@type": "Country", "name": "Iran"},
    }
    if CONTACT["postal_code"]:
        node["address"]["postalCode"] = CONTACT["postal_code"]
    # Only publish coordinates when they are real. A wrong pin is worse than none.
    if CONTACT["latitude"] and CONTACT["longitude"]:
        node["geo"] = {"@type": "GeoCoordinates",
                       "latitude": CONTACT["latitude"],
                       "longitude": CONTACT["longitude"]}
    sa = sameas()
    if sa:
        node["sameAs"] = sa
    return node


def website_ld():
    return {"@context": "https://schema.org", "@type": "WebSite",
            "@id": BASE + "/#website", "url": BASE + "/",
            "name": SITE["name_fa"], "inLanguage": "fa-IR",
            "publisher": {"@id": BASE + "/#org"}}


def offer_ld(p):
    """Offer node. Prices are Rial + IRR (ISO 4217); Toman has no ISO code.
    Products with no price get no Offer at all rather than a fake one."""
    if p["price_irr"] is None:
        return None
    # priceValidUntil is deliberately omitted. It is only "recommended", but a
    # date in the PAST actively suppresses the listing — so a generator that
    # stamps build_date+30d silently kills every rich result the first month
    # nobody rebuilds.
    return {
        "@type": "Offer",
        "url": BASE + p["url"],
        # Rial, exactly as stored. IRR is the only ISO 4217 code for Iran;
        # Toman (the unit we DISPLAY) has no ISO code and Google rejects it.
        # Display divides by 10 — see money() — the markup never does.
        "price": p["price_irr"],
        "priceCurrency": "IRR",
        "availability": ("https://schema.org/InStock" if p["in_stock"]
                         else "https://schema.org/OutOfStock"),
        "itemCondition": "https://schema.org/NewCondition",
        "seller": {"@id": BASE + "/#org"},
    }


def product_ld(p):
    b = BRANDS[p["brand"]]
    node = {
        "@context": "https://schema.org", "@type": "Product",
        "@id": BASE + p["url"] + "#product",
        "name": p["title"],
        "sku": p["sku"],
        "category": CATEGORIES[p["category"]]["fa"],
        "url": BASE + p["url"],
        "image": [BASE + f"/assets/img/{p['image']}-{img_w(p['image'], 700)}.jpg"],
        "description": product_description(p, plain=True),
        # `brand` is the PART MANUFACTURER (ASMCO), never the car make. The
        # catalogue's own "brand" field is the vehicle the part fits — emitting
        # "brand": "MVM" on a brake disc would assert MVM made it, which is
        # false and is exactly the misleading markup that earns a manual
        # action. The car is expressed through isAccessoryOrSparePartFor.
        "brand": {"@type": "Brand", "name": SUPPLIER["part_brand"]},
        "isAccessoryOrSparePartFor": {
            "@type": "Vehicle",
            "name": f"{b['fa']} {p['model']}".strip(),
            "manufacturer": {"@type": "Organization", "name": b["fa"]},
        },
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "موقعیت نصب",
             "value": AXLE_FA[p["axle"]]},
            {"@type": "PropertyValue", "name": "خودرو",
             "value": f"{b['fa']} {p['model']}".strip()},
        ],
    }
    # TRA-X and XTRA are ASMCO product LINES, not brands of their own.
    if p["variant"] != "base":
        node["additionalProperty"].append(
            {"@type": "PropertyValue", "name": "سری محصول",
             "value": VARIANTS[p["variant"]]["code"]})
    # No `mpn` and no `gtin`: we do not have manufacturer part numbers, and
    # repeating our own SKU as an MPN would be a fabricated identifier.
    # No `aggregateRating`: there are zero reviews, and inventing one is a
    # domain-wide manual-action risk.
    off = offer_ld(p)
    if off:
        node["offers"] = off
    return node


def product_description(p, plain=False):
    """Unique per-product prose. Not boilerplate: it varies by category,
    axle, variant and whether the part is a friction or a rotating part."""
    b = BRANDS[p["brand"]]["fa"]
    cat = CATEGORIES[p["category"]]["fa"]
    axle = AXLE_FA[p["axle"]]
    model = (" " + p["model"]) if p["model"] else ""
    v = VARIANTS[p["variant"]]
    bits = [f"{cat} {axle} مناسب {b}{model}، با کد کالای {p['sku']}."]
    if p["category"] == "brake-pads":
        bits.append(
            f"لنت ترمز {axle} یکی از پرمصرف‌ترین قطعات مصرفی خودرو است و مستقیماً "
            f"روی فاصله توقف خودرو اثر می‌گذارد. این لنت برای {b}{model} طراحی شده "
            f"و ابعاد و شکل آن با کالیپر همان خودرو مطابقت دارد.")
        bits.append(
            "لنت ترمز را همیشه به‌صورت جفت (هر دو چرخ یک محور) تعویض کنید؛ "
            "تعویض تک‌طرفه باعث کشیده‌شدن خودرو به یک سمت هنگام ترمزگیری می‌شود.")
    elif p["category"] == "brake-discs":
        bits.append(
            f"دیسک چرخ {axle} سطحی است که لنت روی آن فشرده می‌شود و گرمای ترمزگیری "
            f"را دفع می‌کند. این دیسک برای {b}{model} ساخته شده است.")
        if p["variant"] == "tra-x":
            bits.append(
                "مدل TRA-X سوراخ‌دار است. سوراخ‌ها گازها و گردوغبار حاصل از "
                "سایش لنت را از سطح تماس خارج می‌کنند و به خنک‌شدن سریع‌تر دیسک "
                "کمک می‌کنند؛ نتیجه، کاهش افت ترمز در ترمزگیری‌های پی‌درپی است.")
        elif p["variant"] == "xtra":
            bits.append(
                "مدل XTRA هم سوراخ‌دار و هم شیاردار است. شیارها لایه گازی بین لنت "
                "و دیسک را می‌شکنند و سطح لنت را تمیز نگه می‌دارند؛ مناسب رانندگی "
                "پرترمز شهری و مسیرهای کوهستانی.")
        else:
            bits.append(
                "این مدل سطح صاف استاندارد دارد؛ گزینه متعادل برای رانندگی "
                "روزمره شهری و جاده‌ای با کمترین صدا.")
        bits.append(
            "دیسک را همیشه جفت تعویض کنید و پس از تعویض، لنت نو را طبق دستور "
            "سازنده آب‌بندی کنید.")
    else:
        bits.append(
            f"کاسه چرخ {axle} در سیستم ترمز کفشکی به کار می‌رود و کفشک‌های ترمز "
            f"از داخل به دیواره آن فشار می‌آورند. این کاسه چرخ مخصوص {b}{model} است.")
        bits.append(
            "خط‌افتادگی یا بیضی‌شدن کاسه چرخ باعث لرزش پدال ترمز دستی و کاهش "
            "اثر ترمز عقب می‌شود.")
    if plain:
        return " ".join(bits)
    return "".join(f"<p>{e(x)}</p>" for x in bits)


def price_block(p, big=False):
    # DESIGN.md §10: a price we do not hold is «استعلام تلفنی» — never
    # «تماس بگیرید» on its own, and never a fabricated figure.
    if p["price_irr"] is None:
        return ('<div class="price-na">استعلام تلفنی</div>' if big
                else '<div class="price na">استعلام تلفنی</div>')
    toman = money(p["price_irr"], data=True)
    rial = to_fa_digits(f"{p['price_irr']:,}").replace(",", "،")
    if big:
        return (f'<div class="price-main">{toman}</div>'
                f'<div class="price-alt">معادل {rial} ریال</div>')
    return f'<div class="price">{toman}</div>'


def price_chip(p, *, size="sm"):
    """The delta chip beside a price.

    Direction colour is "is this good for the BUYER" — a price going UP is bad
    news for someone buying a brake disc, so up wears the warning tone and down
    wears the good tone. That is the opposite of a stock ticker and it is the
    right way round here.

    Always icon + text, never colour alone: the status palette is sub-3:1 on a
    light surface by design and the pairing is the mitigation, so this still
    reads under full colour-vision deficiency and in forced-colors mode.
    """
    st = p.get("price") or {}
    d = st.get("direction")
    if d in (None, "none", "new"):
        # One observation, or none. No trend exists, so none is claimed.
        if st.get("latest_date"):
            return (f'<span class="chip-price is-new" title="نخستین قیمت ثبت‌شده">'
                    f'<span aria-hidden="true">●</span> ثبت‌شده '
                    f'{e(to_fa_digits(PR.jalali_str(st["latest_date"], with_year=False)))}'
                    f'</span>')
        return ""
    pct = abs(st["change_pct"])
    # A 0.05% move rounds to "0%", and "▼ 0% decrease" reads as no change at
    # all — actively misleading. Below the rounding floor, say so explicitly
    # rather than print a zero.
    # U+066B ARABIC DECIMAL SEPARATOR, matching the U+066C thousands
    # separator used for prices. A Latin "." beside Persian digits is wrong.
    num = ("کمتر از ۰٫۱" if pct < 0.05
           else to_fa_digits(f"{pct:.1f}".rstrip("0").rstrip("."))
                 .replace(".", "\u066B"))
    if d == "flat":
        return ('<span class="chip-price is-flat">'
                '<span aria-hidden="true">=</span> بدون تغییر</span>')
    arrow = "▲" if d == "up" else "▼"
    word = "افزایش" if d == "up" else "کاهش"
    cls = "is-up" if d == "up" else "is-down"
    days = to_fa_digits(st.get("span_days") or 0)
    return (f'<span class="chip-price {cls}" '
            f'title="{e(word)} نسبت به {days} روز پیش">'
            f'<span aria-hidden="true">{arrow}</span> '
            f'<bdi>{num}٪</bdi> <span class="chip-word">{word}</span></span>')


# DESIGN.md §14.3: the slider's rows are 340px and the grid's are 283px, so
# they need different `sizes`. Sharing one string would either under-resolve
# the slider photo or make 77 grid rows over-fetch a 700px rendition.
GRID_SIZES = "(min-width:1000px) 283px, (min-width:700px) 245px, 45vw"
SLIDER_SIZES = "(min-width:1000px) 340px, (min-width:700px) 300px, 78vw"


def card(p, eager=False, sizes=GRID_SIZES):
    b = BRANDS[p["brand"]]
    # Three different facts, three different treatments. They used to share
    # one .badge slot on the image, so a stock WARNING and a product-LINE
    # marker wore the same costume — and because the slot was exclusive, a
    # product could not be both out of stock and TRA-X.
    #   out of stock  -> a warning, on the image, in --rise
    #   product line  -> a spec, in the tag row, solid on --board
    #   brand/fitment -> attributes, in the tag row, quieter
    badge = '<span class="badge">ناموجود</span>' if not p["in_stock"] else ""
    line, disp = "", p["title"]
    if p["variant"] != "base":
        code = VARIANTS[p["variant"]]["code"]
        line = (f'<span class="line" title="{e(VARIANTS[p["variant"]]["fa"])}">'
                f'{bdi(code)}</span>')
        # The canonical title already ends in the variant code, so with the
        # chip present it was printed twice in one card. The chip carries it
        # here; the <h1> and every machine-readable field keep the full name.
        if disp.endswith(" " + code):
            disp = disp[: -(len(code) + 1)]
    img = p["image"]
    # The price slot and the button must not say the same words: without a
    # price the card was printing «استعلام قیمت» twice, once as the figure and
    # once as the label.
    cta = ('<a class="add" href="{}">مشاهده و سفارش</a>'.format(e(p["url"]))
           if p["price_irr"] is not None else
           '<a class="add na" href="{}">مشاهده و استعلام</a>'.format(e(p["url"])))
    return f'''<article class="card" data-brand="{e(p["brand"])}" data-axle="{e(p["axle"])}"
         data-price="{p["price_irr"] if p["price_irr"] is not None else ""}"
         data-title="{e(p["title"])}" data-search="{e(p["search"])}">
  <div class="ph">{badge}
    {picture(img, alt="", box=340, sizes=sizes, eager=eager)}
  </div>
  <div class="body">
    <h3><a href="{e(p["url"])}">{latin_bdi(disp)}</a></h3>
    <div class="tags">
      <span class="sku">{bdi(p["sku"])}</span>
      {line}
      <span class="brand">{e(b["fa"])}</span>
      <span class="fit">{e(AXLE_FA[p["axle"]])}</span>
    </div>
    {price_block(p)}
    <div class="card-trend">{price_chip(p)}{PR.sparkline(p.get("price", {}).get("history", []))}</div>
    {cta}
  </div>
</article>'''


# ------------------------------------------------------------------ product
def related(p, all_p, n=8):
    """Same car first (the other axle, other variants), then same category+brand."""
    def key(x):
        score = 0
        if x["brand"] == p["brand"] and x["model"] == p["model"]:
            score += 100
            if x["category"] == p["category"]:
                score += 20
        elif x["brand"] == p["brand"]:
            score += 40
            if x["category"] == p["category"]:
                score += 10
        elif x["category"] == p["category"]:
            score += 5
        if x["in_stock"]:
            score += 2
        return -score
    pool = [x for x in all_p if x["sku"] != p["sku"]]
    return sorted(pool, key=key)[:n]


def product_faq(p):
    b = BRANDS[p["brand"]]["fa"]
    model = (" " + p["model"]) if p["model"] else ""
    cat = CATEGORIES[p["category"]]["fa"]
    axle = AXLE_FA[p["axle"]]
    qa = [(
        f"این {cat} به {b}{model} می‌خورد؟",
        f"بله. این کالا با کد {p['sku']} مخصوص محور {axle} {b}{model} است. "
        f"اگر از سال ساخت یا تیپ خودروی خود مطمئن نیستید، شماره شاسی یا کارت "
        f"خودرو را برای ما بفرستید تا تطابق قطعه را بررسی کنیم."
    ), (
        f"{cat} را جفت بخرم یا تکی؟",
        "همیشه جفت. قطعات ترمز باید روی هر دو چرخ یک محور هم‌زمان تعویض شوند؛ "
        "در غیر این صورت نیروی ترمز دو طرف برابر نیست و خودرو هنگام ترمز به یک "
        "سمت کشیده می‌شود. قیمت درج‌شده برای یک عدد است، مگر آنکه غیر از این ذکر شده باشد."
    )]
    if p["category"] == "brake-pads":
        qa.append(("چه زمانی باید لنت ترمز را عوض کرد؟",
                   "وقتی ضخامت لایه اصطکاکی به حدود ۳ میلی‌متر برسد، یا وقتی صدای "
                   "سوت و جیر هنگام ترمز شنیده می‌شود، یا پدال ترمز نرم‌تر از حالت "
                   "عادی شده است. به‌طور میانگین هر ۳۰ تا ۵۰ هزار کیلومتر، بسته به "
                   "سبک رانندگی."))
    elif p["category"] == "brake-discs":
        qa.append(("لرزش فرمان هنگام ترمز نشانه چیست؟",
                   "معمولاً تاب‌برداشتن یا ناهمواری سطح دیسک چرخ. اگر ضخامت دیسک "
                   "هنوز بالاتر از حد مجاز سازنده باشد می‌توان آن را تراش داد، اما "
                   "اگر به حداقل ضخامت رسیده باشد باید تعویض شود."))
    else:
        qa.append(("تفاوت کاسه چرخ با دیسک چرخ چیست؟",
                   "در ترمز کاسه‌ای، کفشک‌ها از داخل به دیواره کاسه فشار می‌آورند؛ "
                   "در ترمز دیسکی، لنت‌ها از دو طرف روی دیسک فشرده می‌شوند. "
                   "بیشتر خودروهای امروزی جلو دیسکی و عقب کاسه‌ای هستند."))
    if p["price_irr"] is None:
        qa.append(("چرا قیمت این کالا درج نشده؟",
                   "قیمت این قطعه بسته به موجودی و نرخ روز تغییر می‌کند. برای "
                   "استعلام قیمت لحظه‌ای با ما تماس بگیرید."))
    return qa


def faq_block(qa):
    items = "".join(
        f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    return f'<section class="faq"><h2>پرسش‌های پرتکرار</h2>{items}</section>'


def faq_ld(qa):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in qa]}


def quote_block(p):
    """The quote line: last, week's change, range since tracking began, and
    how many observations stand behind it.

    This is what an instrument page carries on any exchange, and it is the
    part that turns "a price" into "a price with a provenance". Every figure
    here is derived from the observation record — nothing is asserted that the
    record does not contain, so a product with one observation shows the
    observation count and nothing else.
    """
    st = p.get("price") or {}
    if not st.get("points"):
        return ""
    def cell(label, value):
        return (f'<div><span class="q-label">{e(label)}</span>'
                f'<span class="q-val">{value}</span></div>')
    cells = []
    if st.get("points", 0) >= 2:
        pct = st.get("change_pct", 0.0)
        arrow = "▲" if pct > 0 else "▼" if pct < 0 else "="
        cls = "is-up" if pct > 0 else "is-down" if pct < 0 else "is-flat"
        n = ("کمتر از ۰٫۱" if abs(pct) < 0.05
             else to_fa_digits(f"{abs(pct):.1f}").replace(".", "\u066B"))
        cells.append(cell(f'تغییر {to_fa_digits(st.get("span_days") or 0)} روز',
                          f'<span class="chip-price {cls}">'
                          f'<span aria-hidden="true">{arrow}</span> '
                          f'<bdi>{n}٪</bdi></span>'))
        cells.append(cell("کمترین", money(st["low"], unit=False)))
        cells.append(cell("بیشترین", money(st["high"], unit=False)))
        cells.append(cell("از تاریخ",
                          to_fa_digits(PR.jalali_str(st["first_date"]))))
    cells.append(cell("تعداد ثبت", to_fa_digits(st["points"])))
    return f'<div class="quote">{"".join(cells)}</div>'


def price_history_block(p):
    """The per-product price story. Empty until two observations exist."""
    st = p.get("price") or {}
    if st.get("points", 0) < 2:
        if not st.get("latest_date"):
            return ""
        return (f'<p class="hist-none">قیمت این کالا از '
                f'{e(to_fa_digits(PR.jalali_str(st["latest_date"])))} ثبت می‌شود. '
                f'نمودار تغییر قیمت پس از نخستین تغییر نمایش داده خواهد شد.</p>')
    span = (f'{to_fa_digits(PR.jalali_str(st["first_date"], with_year=False))}'
            f' تا {to_fa_digits(PR.jalali_str(st["latest_date"], with_year=False))}')
    return f'''<section class="hist">
  <h2>روند قیمت</h2>
  <p class="hist-span">{e(span)} — کمترین {money(st["low"], unit=False)} /
     بیشترین {money(st["high"], unit=False)} تومان</p>
  {PR.history_chart(st["history"])}
  <details class="hist-details">
    <summary>نمایش جدول تاریخچه قیمت</summary>
    {PR.history_table(st["history"])}
  </details>
</section>'''


def product_page(p, all_p):
    b = BRANDS[p["brand"]]
    cat = CATEGORIES[p["category"]]
    axle = AXLE_FA[p["axle"]]
    model = (" " + p["model"]) if p["model"] else ""
    v = VARIANTS[p["variant"]]

    title = f"{p['title']} | قیمت و خرید | {SITE['brand_suffix']}"
    if p["price_irr"] is not None:
        desc = (f"خرید {p['title']} با کد {p['sku']}. قیمت روز، اصالت کالا و "
                f"ارسال به سراسر ایران. مشاوره فنی رایگان برای انتخاب قطعه {b['fa']}.")
    else:
        desc = (f"{p['title']} با کد {p['sku']}. برای استعلام قیمت روز و موجودی "
                f"تماس بگیرید. مشاوره فنی رایگان برای انتخاب قطعه {b['fa']}.")

    cr = [("/", "خانه"), (f"/{p['category']}/", cat["fa"]),
          (f"/brands/{p['brand']}/", b["fa"]), (None, p["title"])]

    qa = product_faq(p)
    wa = SOCIAL.get("whatsapp") or CONTACT["whatsapp"]
    stock_cls = "" if p["in_stock"] else " out"
    stock_txt = "موجود در انبار" if p["in_stock"] else "ناموجود / استعلام موجودی"

    spec_rows = [
        ("برند", SUPPLIER["part_brand"]),
        ("دسته‌بندی", cat["fa"]),
        ("خودرو", f"{b['fa']}{model}".strip()),
        ("محور", axle),
        ("مدل محصول", v["fa"]),
        ("کد کالا", p["sku"]),
    ]
    LATIN_CELLS = {"کد کالا", "برند"}
    spec = "".join(
        f'<tr><th scope="row">{e(k)}</th>'
        f'<td>{bdi(val) if k in LATIN_CELLS else e(val)}</td></tr>'
        for k, val in spec_rows)

    rel = related(p, all_p, n=12)


    jsonld = [product_ld(p), crumbs_ld(cr), faq_ld(qa), org_ld()]

    return f'''{head(title=title, description=desc, canonical=p["url"],
                     jsonld=jsonld, og_type="product")}
{header()}
{crumbs(cr)}
<main id="main">
<!-- The board, once per page (DESIGN.md §8). On a product page it carries
     this product's own price at --t-figure, its stamp, and the two actions —
     so the name, the number and the phone button are the first thing seen,
     above the photograph rather than beside it. -->
<section class="board-band bb-split" aria-labelledby="p-h">
  <div class="wrap">
    <div class="bb-lede">
      <h1 id="p-h">{latin_bdi(p["title"])}</h1>
      <p class="sub">{bdi(SUPPLIER["part_brand"])} · کد کالا: {bdi(p["sku"])} — {e(v["fa"])}</p>
      <span class="stock{stock_cls}">{e(stock_txt)}</span>
    </div>
    <div class="bb-table">
      <div class="price-box">
        {price_block(p, big=True)}
        <div class="price-row">{price_chip(p)}</div>
      </div>
      {quote_block(p)}
      <div class="cta">
        <a class="call" href="tel:{e(CONTACT["phone_tel"])}">تماس و سفارش {bdi(CONTACT["phone_display"])}</a>
        <a class="wa" href="https://wa.me/{e(wa)}?text={e("سلام، درباره " + p["title"] + " (" + p["sku"] + ") سوال داشتم.")}"
           rel="noopener" target="_blank">سفارش در واتساپ</a>
      </div>
    </div>
  </div>
</section>

<div class="wrap">
  <div class="product">
    <div class="gallery">
      {picture(p["image"], alt=p["title"], box=380,
               sizes="(min-width:760px) 380px, 92vw", eager=True)}
    </div>

    <div class="info">
      {price_history_block(p)}

      <table class="spec">
        <caption>مشخصات فنی</caption>
        <tbody>{spec}</tbody>
      </table>

      <div class="prose">
        <h2>توضیحات</h2>
        {product_description(p)}
      </div>
    </div>
  </div>

  {faq_block(qa)}
</div>

<div class="wrap">
  {slider(rel, title_html=f"<b>قطعات مرتبط</b> برای {e(b['fa'])}{e(model)}",
          label="قطعات مرتبط", slug="rel")}
</div>
</main>
{footer()}'''


# ----------------------------------------------------------------- listings
def itemlist_ld(prods, name, url):
    return {"@context": "https://schema.org", "@type": "ItemList",
            "name": name, "url": BASE + url,
            "numberOfItems": len(prods),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1,
                 "url": BASE + p["url"], "name": p["title"]}
                for i, p in enumerate(prods)]}


def filter_bar(prods, brands_present):
    opts = "".join(
        f'<option value="{e(s)}">{e(BRANDS[s]["fa"])}</option>'
        for s in sorted(brands_present, key=lambda s: BRANDS[s]["fa"]))
    return f'''<div class="filters">
  <div class="row">
    <label class="sr-only" for="q">جستجو در این دسته</label>
    <input type="search" id="q" placeholder="جستجوی نام محصول یا کد کالا" autocomplete="off">
    <label class="sr-only" for="fb">فیلتر خودرو</label>
    <select id="fb"><option value="">همه خودروها</option>{opts}</select>
    <label class="sr-only" for="fa">فیلتر محور</label>
    <select id="fa"><option value="">جلو و عقب</option><option value="front">جلو</option><option value="rear">عقب</option></select>
    <label class="sr-only" for="fs">مرتب‌سازی</label>
    <select id="fs">
      <option value="">مرتب‌سازی پیش‌فرض</option>
      <option value="asc">ارزان‌ترین</option>
      <option value="desc">گران‌ترین</option>
      <option value="name">نام محصول</option>
    </select>
  </div>
  <p class="result-count" id="count" role="status" aria-live="polite"></p>
</div>'''


def category_page(slug, prods, all_p):
    c = CATEGORIES[slug]
    url = f"/{slug}/"
    n = len(prods)
    brands_present = sorted({p["brand"] for p in prods})
    brand_names = "، ".join(BRANDS[b]["fa"] for b in
                            sorted(brands_present, key=lambda s: -sum(1 for p in prods if p["brand"] == s))[:8])
    title = f"{c['h1']} | قیمت روز و خرید | {SITE['brand_suffix']}"
    desc = (f"خرید {c['fa']} برای {brand_names} با قیمت روز. "
            f"{to_fa_digits(n)} کالا، جلو و عقب، مشاوره فنی و ارسال به سراسر ایران.")
    cr = [("/", "خانه"), (None, c["fa"])]

    priced = [p for p in prods if p["price_irr"]]
    lo = min(priced, key=lambda p: p["price_irr"])["price_irr"] if priced else None
    hi = max(priced, key=lambda p: p["price_irr"])["price_irr"] if priced else None
    rng = (f"محدوده قیمت: از {money(lo, unit=False)} تا {money(hi, unit=False)} تومان"
           if priced else "")

    qa = category_faq(slug, brand_names)
    jsonld = [
        {"@context": "https://schema.org", "@type": "CollectionPage",
         "name": c["h1"], "url": BASE + url, "inLanguage": "fa-IR",
         "description": c["blurb"], "isPartOf": {"@id": BASE + "/#website"},
         "publisher": {"@id": BASE + "/#org"}},
        itemlist_ld(prods, c["h1"], url), crumbs_ld(cr), faq_ld(qa), org_ld()]

    brand_links = " ".join(
        f'<a href="/brands/{e(b)}/">{e(BRANDS[b]["fa"])}</a>'
        for b in sorted(brands_present, key=lambda s: BRANDS[s]["fa"]))

    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld)}
{header(url)}
{crumbs(cr)}
<main id="main">
<section class="board-band page-head"><div class="wrap">
  <h1>{e(c["h1"])}</h1>
  <p>{e(c["blurb"])} — {e(brand_names)} و دیگر خودروهای چینی.</p>
  <p class="meta">{to_fa_digits(n)} کالا در این دسته{(" — " + rng) if rng else ""}</p>
</div></section>

<div class="wrap shop">
  <h2 class="sr-only">فهرست محصولات</h2>
  {filter_bar(prods, brands_present)}
  <div class="grid-products lattice" id="grid">{"".join(card(p) for p in prods)}</div>
  <p class="empty" id="empty" hidden>کالایی با این مشخصات پیدا نشد. فیلترها را تغییر دهید یا با ما تماس بگیرید.</p>
</div>

<div class="wrap">
  {faq_block(qa)}
  <section class="faq">
    <h2>{e(c["fa"])} بر اساس خودرو</h2>
    <p class="brandlinks">{brand_links}</p>
  </section>
</div>
</main>
{footer()}'''


def category_faq(slug, brand_names):
    if slug == "brake-pads":
        return [
            ("لنت ترمز مناسب خودروی من کدام است؟",
             f"لنت ترمز بر اساس مدل خودرو و محور (جلو یا عقب) انتخاب می‌شود. "
             f"در این صفحه لنت‌های موجود برای {brand_names} را می‌بینید. اگر مطمئن "
             f"نیستید، کارت خودرو یا شماره شاسی را برای ما بفرستید."),
            ("لنت ترمز چند وقت یک‌بار عوض می‌شود؟",
             "به‌طور میانگین هر ۳۰ تا ۵۰ هزار کیلومتر، اما سبک رانندگی تعیین‌کننده "
             "است. رانندگی شهری پرترافیک عمر لنت را تا نصف کاهش می‌دهد."),
            ("علائم خرابی لنت ترمز چیست؟",
             "صدای سوت یا جیر هنگام ترمز، افزایش فاصله توقف، لرزش پدال، کشیده‌شدن "
             "خودرو به یک سمت، و روشن‌شدن چراغ هشدار ترمز."),
            ("لنت جلو و عقب را باید با هم عوض کرد؟",
             "نه لزوماً. لنت جلو معمولاً دو تا سه برابر سریع‌تر از عقب مصرف می‌شود. "
             "اما هر محور باید جفت تعویض شود."),
        ]
    if slug == "brake-discs":
        return [
            ("تفاوت دیسک ساده، سوراخ‌دار (TRA-X) و شیاردار (XTRA) چیست؟",
             "دیسک ساده برای رانندگی روزمره کافی است. مدل سوراخ‌دار TRA-X گرما و "
             "گاز را بهتر دفع می‌کند و برای ترمزگیری‌های پی‌درپی مناسب‌تر است. "
             "مدل XTRA هم سوراخ و هم شیار دارد و بیشترین مقاومت در برابر افت ترمز "
             "را ارائه می‌دهد."),
            ("دیسک چرخ را تراش بدهم یا تعویض کنم؟",
             "اگر ضخامت دیسک بالاتر از حداقل مجاز سازنده باشد، تراش گزینه مقرون‌به‌صرفه‌ای "
             "است. اگر به حداقل ضخامت رسیده یا ترک خورده باشد، حتماً باید تعویض شود."),
            ("لرزش فرمان هنگام ترمز از کجاست؟",
             "معمولاً تاب‌برداشتن دیسک چرخ جلو. گرمای زیاد و خنک‌شدن ناگهانی (مثلاً "
             "عبور از آب پس از ترمز شدید) عامل رایج آن است."),
            ("دیسک را جفت بخرم؟",
             "بله. تعویض تک دیسک روی یک محور باعث اختلاف نیروی ترمز و کشیده‌شدن "
             "خودرو می‌شود."),
        ]
    return [
        ("کاسه چرخ چیست و چه فرقی با دیسک دارد؟",
         "در ترمز کاسه‌ای، کفشک‌ها از داخل به دیواره کاسه فشار می‌آورند. در ترمز "
         "دیسکی، لنت‌ها از بیرون روی دیسک فشرده می‌شوند. بیشتر خودروهای چینی "
         "محور عقب کاسه‌ای دارند."),
        ("علائم خرابی کاسه چرخ چیست؟",
         "کاهش اثر ترمز دستی، صدای خش‌خش از چرخ عقب، لرزش هنگام ترمزگیری آرام، "
         "و خط‌افتادگی قابل مشاهده روی سطح داخلی کاسه."),
        ("کاسه چرخ را باید همراه کفشک عوض کرد؟",
         "توصیه می‌شود. کفشک نو روی کاسه خط‌افتاده به‌درستی جا نمی‌افتد و عمر "
         "کوتاهی خواهد داشت."),
    ]


def brand_page(slug, prods, all_p):
    b = BRANDS[slug]
    url = f"/brands/{slug}/"
    n = len(prods)
    by_cat = {c: [p for p in prods if p["category"] == c] for c in CAT_ORDER}
    by_cat = {k: v for k, v in by_cat.items() if v}
    cats_fa = "، ".join(CATEGORIES[c]["fa"] for c in by_cat)
    models = sorted({p["model"] for p in prods if p["model"]})
    models_fa = "، ".join(models[:10])

    title = f"قطعات ترمز {b['fa']} | لنت، دیسک و کاسه چرخ | {SITE['brand_suffix']}"
    desc = (f"خرید {cats_fa} برای خودروهای {b['fa']}"
            + (f" ({models_fa})" if models_fa else "")
            + f". {to_fa_digits(n)} کالا با قیمت روز و ارسال به سراسر ایران.")
    cr = [("/", "خانه"), ("/brands/", "خودروها"), (None, b["fa"])]
    qa = [
        (f"چه قطعات ترمزی برای {b['fa']} موجود است؟",
         f"در حال حاضر {to_fa_digits(n)} کالا شامل {cats_fa} برای "
         f"{b['fa']} در فروشگاه موجود است."),
        (f"قطعات {b['fa']} اصلی هستند؟",
         "بله. تمام قطعات با تضمین اصالت عرضه می‌شوند. در صورت مغایرت، کالا طبق "
         f"شرایط بازگشت تا {to_fa_digits(COMMERCE['return_days'])} روز قابل مرجوع است."),
        ("چطور مطمئن شوم قطعه به خودروی من می‌خورد؟",
         "مدل و سال ساخت خودرو و محور مورد نظر (جلو یا عقب) را به ما بگویید. "
         "در صورت تردید، شماره شاسی را بفرستید تا تطابق را بررسی کنیم."),
    ]
    jsonld = [itemlist_ld(prods, f"قطعات ترمز {b['fa']}", url), crumbs_ld(cr),
              faq_ld(qa), org_ld()]

    sections = ""
    for c, items in by_cat.items():
        sections += (f'<h2 class="section-title"><span class="st-text">'
                     f'<b>{e(CATEGORIES[c]["fa"])}</b> {e(b["fa"])}</span></h2>'
                     f'<div class="grid-products lattice">{"".join(card(p) for p in items)}</div>'
                     f'<p class="linkrow">'
                     f'<a href="/{e(c)}/">همه {e(CATEGORIES[c]["fa"])} '
                     f'{e(b["fa"])}</a></p>')

    model_list = ("".join(f"<li>{e(m)}</li>" for m in models)) or "<li>—</li>"
    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld)}
{header("/brands/")}
{crumbs(cr)}
<main id="main">
<section class="board-band page-head"><div class="wrap">
  <h1>قطعات ترمز {e(b["fa"])}</h1>
  <p>{e(cats_fa)} برای خودروهای {e(b["fa"])}{(" — مدل‌های " + e(models_fa)) if models_fa else ""}.</p>
  <p class="meta">{to_fa_digits(n)} کالا</p>
</div></section>

<div class="wrap shop">{sections}</div>

<div class="wrap">
  <section class="faq">
    <h2>مدل‌های {e(b["fa"])} که قطعه آن‌ها را داریم</h2>
    <ul class="cols2">{model_list}</ul>
  </section>
  {faq_block(qa)}
</div>
</main>
{footer()}'''


def _base_monogram(en):
    if en.isupper() and len(en) <= 4:
        return en
    parts = [w for w in en.replace("-", " ").split() if w]
    if len(parts) > 1:
        return "".join(w[0] for w in parts[:2]).upper()
    return en[:2].upper()


def _build_monograms():
    """Short marks for every car, guaranteed unique.

    Half these names are already initialisms (MVM, JAC, KMC, FAW) and go
    through whole; the rest give up their initials. Collisions are then
    lengthened one letter at a time — Chery and Changan both reduced to "CH",
    which makes two different cars wear the same mark and is worse than no
    mark at all.
    """
    out = {}
    for slug in BRANDS:
        en = BRANDS[slug].get("en") or slug
        m = _base_monogram(en)
        letters = "".join(c for c in en if c.isalnum()).upper()
        n = len(m)
        while m in out.values() and n < len(letters):
            n += 1
            m = letters[:n]
        out[slug] = m
    return out


MONOGRAMS = _build_monograms()


def monogram(slug):
    return MONOGRAMS.get(slug, slug[:2].upper())


def brand_card(slug, items):
    """One car in the list: mark, name, part count, and which way its prices
    are moving.

    The direction is the point. A list of car names is a menu; a list of car
    names carrying a price direction is a market, and it answers the question
    the page exists for — "are parts for my car getting more expensive?"
    """
    t = PR.brand_trend(items)
    trend = ""
    if t:
        pct = t["change_pct"]
        arrow = "▲" if pct > 0 else "▼" if pct < 0 else "="
        cls = "is-up" if pct > 0 else "is-down" if pct < 0 else "is-flat"
        n = ("کمتر از ۰٫۱" if abs(pct) < 0.05
             else to_fa_digits(f"{abs(pct):.1f}").replace(".", "\u066B"))
        # the mini-index is a ratio around 100, so scale it into the integer
        # range the sparkline expects; only its shape is used
        spark = PR.sparkline([(d, int(v * 1000)) for d, v in t["series"]])
        trend = (f'<span class="chip-price {cls}" '
                 f'title="تغییر میانگین قیمت قطعات این خودرو در هفته گذشته">'
                 f'<span aria-hidden="true">{arrow}</span> <bdi>{n}٪</bdi></span>'
                 f'{spark}')
    return (f'<a href="/brands/{e(slug)}/">'
            f'<span class="b-mark" aria-hidden="true">{e(monogram(slug))}</span>'
            f'<span class="b-body">'
            f'<span class="b-name">{e(BRANDS[slug]["fa"])}</span>'
            f'<small>{to_fa_digits(len(items))} کالا</small></span>'
            f'<span class="b-foot">{trend}</span></a>')


def brands_index(groups):
    url = "/brands/"
    title = f"قطعات ترمز بر اساس خودرو | {SITE['brand_suffix']}"
    desc = ("انتخاب لنت ترمز، دیسک چرخ و کاسه چرخ بر اساس برند خودرو: "
            + "، ".join(BRANDS[s]["fa"] for s in list(groups)[:10]) + " و بیشتر.")
    cr = [("/", "خانه"), (None, "خودروها")]
    cards = "".join(brand_card(s, v)
                    for s, v in sorted(groups.items(), key=lambda kv: -len(kv[1])))
    jsonld = [crumbs_ld(cr), org_ld(),
              {"@context": "https://schema.org", "@type": "CollectionPage",
               "name": title, "url": BASE + url, "inLanguage": "fa-IR"}]
    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld)}
{header(url)}
{crumbs(cr)}
<main id="main">
<section class="board-band page-head"><div class="wrap">
  <h1>قطعات ترمز بر اساس خودرو</h1>
  <p>خودروی خود را انتخاب کنید تا لنت ترمز، دیسک چرخ و کاسه چرخ مناسب آن را ببینید.</p>
</div></section>
<div class="wrap">
  <h2 class="sr-only">فهرست برندهای خودرو</h2>
  <div class="brandgrid lattice">{cards}</div>
</div>
</main>
{footer()}'''


def ticker(prods):
    """A live price ticker under the hero.

    This is the one element that says what the site IS at a glance: prices,
    moving, with dates. The headline claims «قیمت روز» — this shows it.

    Accessibility, because a marquee is easy to get wrong:
      * the duplicate half is aria-hidden, so a screen reader reads each
        product once, not twice;
      * it pauses on hover AND on keyboard focus;
      * under prefers-reduced-motion the animation is dropped entirely and it
        becomes a plain horizontally-scrollable strip;
      * it is never the only route to the data — every item links to its
        product and the band links to the full board.

    The track is forced to `direction: ltr` so the items slide leftward and
    enter from the right, where a Persian reader's eye starts. Each item keeps
    dir="rtl" internally so its own text is laid out correctly.
    """
    if not prods:
        return ""

    def item(x, dup=False):
        st = x.get("price") or {}
        d = st.get("direction")
        if d == "up":
            tone, arrow = "t-up", "▲"
        elif d == "down":
            tone, arrow = "t-down", "▼"
        else:
            tone, arrow = "t-flat", "•"
        if d in ("up", "down"):
            pct = abs(st["change_pct"])
            delta = (("کمتر از ۰٫۱" if pct < 0.05
                      else to_fa_digits(f"{pct:.1f}".rstrip("0").rstrip("."))
                           .replace(".", "\u066B")) + "٪")
        elif st.get("latest_date"):
            delta = to_fa_digits(PR.jalali_str(st["latest_date"], with_year=False))
        else:
            delta = ""
        return (f'<a class="tick {tone}" href="{e(x["url"])}" dir="rtl"'
                + (' aria-hidden="true" tabindex="-1"' if dup else '') + '>'
                f'<span class="tick-name">{latin_bdi(x["title"])}</span>'
                f'<span class="tick-price">{money(x["price_irr"], unit=False)}</span>'
                f'<span class="tick-delta"><span aria-hidden="true">{arrow}</span> {delta}</span>'
                f'</a>')

    half = "".join(item(x) for x in prods)
    return f'''<section class="ticker" aria-label="قیمت روز قطعات">
  <a class="ticker-tag" href="/prices/">
    <span class="dot" aria-hidden="true"></span> قیمت روز
  </a>
  <div class="ticker-win">
    <div class="ticker-track">{half}{"".join(item(x, dup=True) for x in prods)}</div>
  </div>
  <a class="ticker-all" href="/prices/">جدول کامل ›</a>
</section>'''


def stat_band(all_p, groups):
    """Four numbers that establish scale and freshness. Not a chart — a KPI
    row of plain figures is the right form for a handful of headline values,
    and it is the cheapest credibility on the page."""
    meta = PRICE_META
    stamp = (to_fa_digits(PR.jalali_str(meta["latest"])) if meta["latest"] else "—")
    ix = meta.get("index") or {}
    cells = [
        (to_fa_digits(len(all_p)), "کالا در انبار"),
        (to_fa_digits(len(groups)), "برند خودرو"),
        (to_fa_digits(meta["observations"]), "قیمت ثبت‌شده"),
        (stamp, "آخرین بروزرسانی"),
    ]
    if ix.get("latest"):
        # The index leads: it is the one number that describes the whole
        # catalogue rather than a count of it.
        cells.insert(0, (to_fa_digits(f"{ix['latest']:.1f}").replace(".", "\u066B"),
                         "شاخص قیمت"))
    return ('<section class="stat-band"><div class="wrap"><ul class="lattice">'
            + "".join(f'<li><b>{e(v)}</b><span>{e(k)}</span></li>'
                      for v, k in cells)
            + "</ul></div></section>")


def slider(prods, *, title_html, label, slug="s1", eager_first=0):
    """A scroll-snap product carousel.

    Deliberately built on native scrolling rather than a JS slider:

      * every product is real HTML in the document, so crawlers see all of
        them whether or not the script runs;
      * with JS off it is still a usable horizontal scroller, and on touch it
        is a native swipe with real momentum — no library can match that feel;
      * `scroll-snap-type` does the paging in CSS, so there is no rAF loop and
        nothing to jank.

    The script only adds the arrows, the progress bar and the keyboard
    shortcuts on top.
    """
    cards = "".join(card(p, eager=i < eager_first, sizes=SLIDER_SIZES)
                    for i, p in enumerate(prods))
    return f'''<section class="slider" id="{e(slug)}"
         aria-roledescription="carousel" aria-label="{e(label)}">
  <div class="slider-head">
    <h2 class="section-title"><span class="st-text">{title_html}</span>
      <span class="count">{to_fa_digits(len(prods))} کالا</span></h2>
    <div class="slider-nav" data-for="{e(slug)}" hidden>
      <button type="button" class="s-btn s-prev" aria-label="قطعات قبلی" aria-controls="{e(slug)}-track">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>
      </button>
      <button type="button" class="s-btn s-next" aria-label="قطعات بعدی" aria-controls="{e(slug)}-track">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>
      </button>
    </div>
  </div>

  <div class="slider-track" id="{e(slug)}-track" tabindex="0"
       role="group" aria-label="{e(label)} — برای جابه‌جایی بکشید یا از کلیدهای جهت‌دار استفاده کنید">
    {cards}
  </div>

  <div class="slider-rail" aria-hidden="true" hidden><span class="slider-fill"></span></div>
</section>'''


# --------------------------------------------------------------------- home
def home(all_p, groups):
    """The entry page.

    Structure is the whole argument here (DESIGN.md §8). The board IS the
    hero — a full-bleed dark band carrying the headline, today's biggest move
    at --t-figure, the vehicle finder and ten live prices. Everything below it
    is quiet paper.

    It opens on one photograph (DESIGN.md §14.4) and closes on none. There is
    no photographic hero BEHIND the words: this site has four stock photos for
    130 products and its subject is numbers, so a picture that competed with
    the figure would be lying about what the page is for. The band is a
    separate register above the text — brake lights in smoke, the trade the
    shop is in — and it earns its place by being the only one.
    """
    url = "/"
    title = f"{SITE['name_fa']} | قیمت روز لنت ترمز، دیسک و کاسه چرخ خودروهای چینی"
    desc = SITE["description"]
    cr = [(None, "خانه")]

    counts = {c: sum(1 for p in all_p if p["category"] == c) for c in CAT_ORDER}
    # brake-drums borrows a disc photo. The draft's third card was a چراغ
    # (headlight) card and its photo came with it — a headlight standing in for
    # brake drums is actively misleading, whereas a disc at least shows a brake
    # part. Still a placeholder: a real کاسه چرخ photo is on the owner's list.
    cat_imgs = {"brake-pads": "cat-brake-pads", "brake-discs": "cat-brake-discs",
                "brake-drums": "cat-brake-drums"}
    cats_html = ""
    for c in CAT_ORDER:
        cc = CATEGORIES[c]
        cats_html += f'''<article class="cat">
      <div>
        <h3><a href="/{e(c)}/">{e(cc["fa"])}</a></h3>
        <p class="cat-count">{to_fa_digits(counts[c])} کالا</p>
      </div>
      <div class="thumb">
        {picture(cat_imgs[c], alt=cc["fa"], box=96, sizes="96px",
                 eager=(c == CAT_ORDER[0]))}
      </div>
    </article>'''

    # Vehicle finder — real options built from the catalogue, wired to real URLs.
    brand_opts = "".join(
        f'<option value="{e(s)}">{e(BRANDS[s]["fa"])}</option>'
        for s in sorted(groups, key=lambda s: BRANDS[s]["fa"]))
    cat_opts = "".join(f'<option value="{e(c)}">{e(CATEGORIES[c]["fa"])}</option>'
                       for c in CAT_ORDER)

    # A slider holds more than a grid row can, so show a real selection: the
    # priced, in-stock items spread across all three categories rather than the
    # first fifteen rows of the catalogue (which were all drums and discs).
    def _spread(items, n):
        """Pick n products that read as a real selection.

        Two constraints, both for the same reason. Spread across the three
        categories, so the strip is not fifteen discs. And never let two
        adjacent rows carry the SAME photograph — with four stock images for
        130 products the naive pick put the identical disc shot in rows two
        and three, which is the single thing that made the strip look
        generated. Rotating the image breaks the repeat at zero cost; it is
        not a substitute for real photography (docs/PLACEHOLDERS.md).
        """
        by_cat = {}
        for x in items:
            by_cat.setdefault(x["category"], []).append(x)
        out = []
        while len(out) < n and any(by_cat.values()):
            progressed = False
            for c in CAT_ORDER:
                pool = by_cat.get(c) or []
                if not pool:
                    continue
                last_img = out[-1]["image"] if out else None
                pick = next((i for i, x in enumerate(pool)
                             if x["image"] != last_img), 0)
                out.append(pool.pop(pick))
                progressed = True
                if len(out) == n:
                    break
            if not progressed:
                break
        return out
    featured = _spread([p for p in all_p if p["in_stock"]], 15)

    priced = [x for x in all_p if x["price_irr"] is not None]
    movers = sorted([x for x in priced
                     if x["price"].get("direction") in ("up", "down")],
                    key=lambda x: -abs(x["price"]["change_pct"]))
    board_pick = (movers or priced)[:10]

    # ---- the headline figure. One per page (DESIGN.md §4), and it is a real
    # measured number with a real product attached to it, not a slogan.
    lead = movers[0] if movers else (priced[0] if priced else None)
    if lead is not None:
        st = lead["price"]
        d = st.get("direction")
        if d in ("up", "down"):
            pct = abs(st["change_pct"])
            num = ("کمتر از ۰٫۱" if pct < 0.05
                   else to_fa_digits(f"{pct:.1f}".rstrip("0").rstrip("."))
                        .replace(".", "\u066B"))
            dcls = "is-up" if d == "up" else "is-down"
            arrow = "▲" if d == "up" else "▼"
            fb_label = f'بیشترین تغییر در {to_fa_digits(st.get("span_days") or 0)} روز گذشته'
            fb_delta = (f'<span class="fb-delta {dcls}">'
                        f'<span aria-hidden="true">{arrow}</span> <bdi>{num}٪</bdi></span>')
        else:
            fb_label = "قیمت ثبت‌شده"
            fb_delta = ""
        figure = f'''<div class="figure-block">
        <span class="fb-label">{e(fb_label)}</span>
        <span class="fb-value">{money(lead["price_irr"], unit=False)}<small>تومان</small></span>
        {fb_delta}
        <span class="fb-name"><a href="{e(lead["url"])}">{latin_bdi(lead["title"])}</a></span>
      </div>'''
    else:
        # Empty state — DESIGN.md §11. A real sentence, never a zero.
        figure = ('<div class="figure-block"><span class="fb-label">قیمت روز</span>'
                  '<span class="fb-name">هنوز قیمتی ثبت نشده است. '
                  'برای استعلام تلفنی تماس بگیرید.</span></div>')

    board_rows = "".join(
        f'<tr><td class="c-name"><a href="{e(x["url"])}">'
        f'<span class="c-thumb">{picture(x["image"], alt="", box=40, sizes="40px")}</span>'
        f'<span>{latin_bdi(x["title"])}</span></a></td>'
        f'<td class="c-price"><data value="{x["price_irr"]}">'
        f'{money(x["price_irr"], unit=False)}</data></td>'
        f'<td class="c-trend">{price_chip(x)}</td>'
        f'<td class="c-spark">{PR.sparkline(x["price"].get("history", []))}</td></tr>'
        for x in board_pick)
    stamp = (to_fa_digits(PR.jalali_str(PRICE_META["latest"]))
             if PRICE_META["latest"] else "")

    qa = [
        ("چطور قطعه مناسب خودروی چینی‌ام را پیدا کنم؟",
         "از جستجوگر بالای صفحه، برند خودرو و نوع قطعه را انتخاب کنید. اگر مدل "
         "دقیق را نمی‌دانید، کارت خودرو یا شماره شاسی را برای ما بفرستید."),
        ("قیمت‌ها به‌روز هستند؟",
         "قیمت‌های درج‌شده قیمت روز است و تاریخ ثبت هر قیمت زیر آن آمده. بازار "
         "قطعات نوسان دارد، پس پیش از سفارش قیمت نهایی را تلفنی یا در واتساپ "
         "تأیید کنید."),
        ("ارسال به شهرستان دارید؟",
         "بله، ارسال به سراسر ایران انجام می‌شود."),
        ("قطعات اصلی هستند یا طرح؟",
         "کالاها با تضمین اصالت عرضه می‌شوند و در صورت مغایرت قابل مرجوع هستند."),
    ]
    jsonld = [org_ld(), website_ld(), faq_ld(qa),
              itemlist_ld(featured, "پرفروش‌ترین قطعات ترمز", "/")]

    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld)}
{header("/")}
<main id="main">
{ticker(board_pick)}

<section class="board-band bb-split bb-lit" aria-labelledby="bb-h">
  <div class="bb-photo" aria-hidden="true">
    {picture("brake-lights", alt="", box=1200, eager=True,
             sizes="(min-width:1200px) 1200px, 100vw")}
  </div>
  <div class="wrap">
    <div class="bb-lede">
      <h1 id="bb-h">قیمت روز قطعات ترمز خودروهای چینی</h1>
      <p class="sub">{e(SUPPLIER["claim_fa"])}. لنت ترمز، دیسک و کاسه چرخ —
        با قیمت روز و تاریخ ثبت، برای {to_fa_digits(len(groups))} برند خودرو.</p>

      {figure}

      <ul class="claims">
        <li><b>ASMCO</b> قطعات اصلی، با تضمین اصالت و امکان مرجوعی</li>
        <li><b>تاریخ‌دار</b> هر قیمت با روز ثبتش نشان داده می‌شود</li>
        <li><b>ارسال</b> به سراسر ایران، سفارش تلفنی و واتساپ</li>
      </ul>
    </div>

    <div class="bb-table">
      <h2 class="bb-th">امروز چه چیزی تغییر کرد</h2>
      <div class="board-scroll">
        <table class="board">
          <caption class="sr-only">قطعاتی که قیمتشان بیش از همه تغییر کرده است</caption>
          <thead><tr>
            <th scope="col">کالا</th><th scope="col">قیمت (تومان)</th>
            <th scope="col">تغییر</th><th scope="col" class="h-spark">روند</th>
          </tr></thead>
          <tbody>{board_rows}</tbody>
        </table>
      </div>
      <a class="board-all" href="/prices/">جدول کامل {to_fa_digits(len(priced))} قیمت</a>
    </div>

    <div class="bb-foot">
      <p class="fd-label" id="fd-label">قطعه خودروی خود را پیدا کنید</p>
      <form class="finder" id="finder" action="/brake-pads/" method="get"
            aria-labelledby="fd-label">
        <label class="sr-only" for="f-brand">خودرو</label>
        <select id="f-brand" name="brand"><option value="">خودرو را انتخاب کنید</option>{brand_opts}</select>
        <label class="sr-only" for="f-cat">نوع قطعه</label>
        <select id="f-cat" name="cat"><option value="">نوع قطعه</option>{cat_opts}</select>
        <label class="sr-only" for="f-axle">محور</label>
        <select id="f-axle" name="axle"><option value="">محور</option><option value="front">جلو</option><option value="rear">عقب</option></select>
        <button type="submit">جستجوی قطعه</button>
      </form>
    </div>
  </div>

</section>

{stat_band(all_p, groups)}

<div class="wrap">
  <h2 class="section-title"><span class="st-text"><b>دسته‌بندی</b>‌های محصولات</span></h2>
  <section class="cats lattice">{cats_html}</section>

  {slider(featured, title_html="<b>پرفروش‌ترین</b> قطعات",
          label="پرفروش‌ترین قطعات ترمز", slug="top", eager_first=3)}
  <p class="linkrow"><a href="/brake-discs/">همه دیسک‌های چرخ</a></p>

  <h2 class="section-title"><span class="st-text"><b>خرید</b> بر اساس خودرو</span></h2>
  <div class="brandgrid lattice">{"".join(brand_card(s, v) for s, v in sorted(groups.items(), key=lambda kv: -len(kv[1])))}</div>

  {faq_block(qa)}
</div>
</main>
{footer()}'''


def index_block(*, on_board=True):
    """The index: level, change, base, and the chart. The most exchange-like
    thing on the site, and the only place --t-figure appears on this page."""
    ix = PRICE_META.get("index") or {}
    ser = PRICE_META.get("index_series") or []
    if not ser:
        return ""
    lvl = to_fa_digits(f"{ix['latest']:.2f}").replace(".", "\u066B")
    since = ix.get("since_base_pct")
    chg = ix.get("change_pct")
    def pct(v):
        if v is None:
            return ""
        arrow = "▲" if v > 0 else "▼" if v < 0 else "="
        cls = "is-up" if v > 0 else "is-down" if v < 0 else "is-flat"
        n = to_fa_digits(f"{abs(v):.2f}").replace(".", "\u066B")
        return (f'<span class="chip-price {cls}">'
                f'<span aria-hidden="true">{arrow}</span> <bdi>{n}٪</bdi></span>')
    base = to_fa_digits(PR.jalali_str(ix["base_date"]))
    return f'''<div class="figure-block ix">
    <span class="fb-label">شاخص قیمت قطعات ترمز</span>
    <span class="fb-value">{lvl}</span>
    <span class="fb-delta">{pct(chg)}</span>
    <span class="fb-name">پایه {e(base)} برابر ۱۰۰ —
      {pct(since)} از آن زمان، میانگین {to_fa_digits(ix["members"])} کالا</span>
  </div>'''


def breadth_strip():
    """How many rose, fell and held in the latest week. The other number every
    exchange board carries, and the one that says the index is an average of
    real movement rather than a single line."""
    b = PRICE_META.get("breadth") or {}
    if not b.get("total"):
        return ""
    span = ""
    if b.get("date") and b.get("prev"):
        span = (f'{to_fa_digits(PR.jalali_str(b["prev"], with_year=False))}'
                f' تا {to_fa_digits(PR.jalali_str(b["date"], with_year=False))}')
    cells = [("گران‌تر", b["up"], "is-up", "▲"),
             ("ارزان‌تر", b["down"], "is-down", "▼"),
             ("بدون تغییر", b["flat"], "is-flat", "=")]
    lis = "".join(
        f'<li class="{cls}"><b><span aria-hidden="true">{ar}</span> '
        f'{to_fa_digits(n)}</b><span>{e(lbl)}</span></li>'
        for lbl, n, cls, ar in cells)
    return (f'<div class="breadth"><p class="bb-th">تغییرات هفته {e(span)}</p>'
            f'<ul>{lis}</ul></div>')


def price_index(products):
    """The exchange page.

    130 rows of numbers is a TABLE, not a chart. Past roughly seven classes
    that all carry meaning, more colour stops helping and a table starts: the
    reader wants to find their part, read its number, and scan for what moved.
    The only colour is the direction of each delta, and it always travels with
    an arrow and a word.

    Above the table sits what makes this a board rather than a price list: the
    index level, the week's breadth, and the index chart.
    """
    url = "/prices/"
    meta = PRICE_META
    tracked = meta["tracked"]
    title = f"شاخص و قیمت روز قطعات ترمز خودروهای چینی | {SITE['brand_suffix']}"
    desc = ("شاخص قیمت و قیمت روز لنت ترمز، دیسک چرخ و کاسه چرخ خودروهای چینی — "
            f"{to_fa_digits(len(products))} کالا با تاریخ آخرین تغییر قیمت.")
    cr = [("/", "خانه"), (None, "قیمت روز")]

    priced = [p for p in products if p["price_irr"] is not None]
    movers = sorted([p for p in priced
                     if p["price"].get("direction") in ("up", "down")],
                    key=lambda p: -abs(p["price"]["change_pct"]))

    last = meta["latest"]
    stamp = (to_fa_digits(PR.jalali_str(last)) if last else "—")

    rows = ""
    for p in sorted(priced, key=lambda p: (p["category"], p["brand"], p["model"])):
        st = p["price"]
        d = st.get("direction", "none")
        # data-* carry machine-sortable values so the column sort in site.js
        # never has to parse Persian digits back into numbers
        pct = st.get("change_pct")
        rows += (
            f'<tr data-cat="{e(p["category"])}" data-brand="{e(p["brand"])}" '
            f'data-dir="{e(d)}" data-price="{p["price_irr"]}" '
            f'data-pct="{pct if pct is not None else ""}" '
            f'data-name="{e(p["title"])}" '
            f'data-search="{e(p["search"])}">'
            f'<td class="c-name"><a href="{e(p["url"])}">'
            f'<span class="c-thumb">{picture(p["image"], alt="", box=40, sizes="40px")}</span>'
            f'<span>{latin_bdi(p["title"])}</span></a></td>'
            f'<td class="c-sku">{bdi(p["sku"])}</td>'
            f'<td class="c-price"><data value="{p["price_irr"]}">'
            f'{money(p["price_irr"], unit=False)}</data></td>'
            f'<td class="c-trend">{price_chip(p)}</td>'
            f'<td class="c-spark">{PR.sparkline(st.get("history", []))}</td>'
            f'<td class="c-date">'
            f'{to_fa_digits(PR.jalali_str(st["latest_date"], with_year=False)) if st.get("latest_date") else "—"}'
            f'</td></tr>')

    if tracked:
        up = [p for p in movers if p["price"]["direction"] == "up"][:1]
        down = [p for p in movers if p["price"]["direction"] == "down"][:1]
        tiles = ""
        for lbl, sel in (("بیشترین افزایش هفته", up), ("بیشترین کاهش هفته", down)):
            if not sel:
                continue
            p = sel[0]
            # The owner's rule, and it is a good one: a price never appears
            # without the thing it is the price of.
            tiles += (f'<div class="tile has-thumb">'
                      f'<div class="t-thumb">'
                      f'{picture(p["image"], alt="", box=72, sizes="72px")}</div>'
                      f'<div class="t-body">'
                      f'<span class="t-label">{e(lbl)}</span>'
                      f'<a class="t-name" href="{e(p["url"])}">{latin_bdi(p["title"])}</a>'
                      f'<span class="t-value">{money(p["price_irr"])}</span>'
                      f'<span class="t-delta">{price_chip(p)}</span>'
                      f'{PR.sparkline(p["price"]["history"])}</div></div>')
        tiles += (f'<div class="tile"><span class="t-label">کالاهای دارای سابقه قیمت</span>'
                  f'<span class="t-value">{to_fa_digits(tracked)}</span>'
                  f'<span class="t-label">از {to_fa_digits(len(priced))} کالای قیمت‌دار — '
                  f'{to_fa_digits(meta["observations"])} قیمت ثبت‌شده</span></div>')
        board_note = ""
    else:
        tiles = ""
        board_note = (
            '<p class="board-note"><b>ثبت قیمت‌ها از امروز آغاز شده است.</b> '
            'نمودار تغییر قیمت و درصد افزایش یا کاهش، از دومین ثبت قیمت به بعد '
            'برای هر کالا نمایش داده می‌شود. تا آن زمان تنها قیمت روز و تاریخ '
            'ثبت آن نشان داده می‌شود — نموداری از داده‌ای که وجود ندارد ساخته نمی‌شود.')

    ix = meta.get("index") or {}
    ix_series = meta.get("index_series") or []
    # The chart's points are hover tooltips, not tab stops, so the keyboard
    # and screen-reader route to the same numbers is this table.
    ix_details = (f'<details class="hist-details ix-details">'
                  f'<summary>نمایش جدول شاخص</summary>'
                  f'{PR.index_table(ix_series)}</details>') if ix_series else ""
    jsonld = [crumbs_ld(cr), org_ld(),
              {"@context": "https://schema.org", "@type": "CollectionPage",
               "name": title, "url": BASE + url, "inLanguage": "fa-IR",
               "description": desc, "publisher": {"@id": BASE + "/#org"}},
              dataset_ld(ix)]

    brand_opts = "".join(
        f'<option value="{e(b)}">{e(BRANDS[b]["fa"])}</option>'
        for b in sorted({p["brand"] for p in priced}, key=lambda s: BRANDS[s]["fa"]))
    cat_opts = "".join(f'<option value="{e(c)}">{e(CATEGORIES[c]["fa"])}</option>'
                       for c in CAT_ORDER)

    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld)}
{header(url)}
{crumbs(cr)}
<main id="main">
<section class="board-band bb-split" aria-labelledby="ix-h">
  <div class="wrap">
    <div class="bb-lede">
      <h1 id="ix-h">بهترین قیمت‌های قطعات ترمز را با عمو چینی پیدا کن</h1>
      <p class="sub">ما به‌روزترین قیمت‌ها را به شما ارائه می‌دهیم.</p>
      {index_block()}
    </div>
    <div class="bb-table">
      {breadth_strip()}
      {PR.index_chart(ix_series)}
      {PR.index_scale(ix_series)}
      {ix_details}
    </div>
  </div>
</section>

<div class="wrap board-page">
  {f'<div class="tiles lattice">{tiles}</div>' if tiles else ''}
  {board_note}

  <div class="filters board-filters">
    <div class="row">
      <label class="sr-only" for="pq">جستجو در جدول قیمت</label>
      <input type="search" id="pq" placeholder="جستجوی نام کالا، خودرو یا کد" autocomplete="off">
      <label class="sr-only" for="pc">دسته‌بندی</label>
      <select id="pc"><option value="">همه دسته‌ها</option>{cat_opts}</select>
      <label class="sr-only" for="pb">خودرو</label>
      <select id="pb"><option value="">همه خودروها</option>{brand_opts}</select>
      <label class="sr-only" for="pd">تغییر قیمت</label>
      <select id="pd">
        <option value="">همه تغییرات</option>
        <option value="up">افزایش‌یافته</option>
        <option value="down">کاهش‌یافته</option>
        <option value="flat">بدون تغییر</option>
      </select>
    </div>
    <p class="result-count" id="pcount" role="status" aria-live="polite"></p>
  </div>

  <div class="board-scroll">
    <table class="board sortable" id="board">
      <caption class="sr-only">جدول قیمت روز قطعات ترمز — برای مرتب‌سازی روی عنوان ستون کلیک کنید</caption>
      <thead>
        <tr>
          <th scope="col" data-sort="name">کالا</th>
          <th scope="col" class="h-sku">کد</th>
          <th scope="col" data-sort="price">قیمت (تومان)</th>
          <th scope="col" data-sort="pct">تغییر</th>
          <th scope="col" class="h-spark">روند</th>
          <th scope="col">تاریخ ثبت</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    <p class="empty" id="pempty" hidden>کالایی با این مشخصات پیدا نشد.</p>
  </div>

  <p class="board-foot">قیمت‌ها به تومان و شامل مالیات بر ارزش افزوده است.
     برای تأیید قیمت نهایی و موجودی، پیش از سفارش
     <a href="/contact/">تماس بگیرید</a>.{_synth_note()}</p>

  <p class="board-foot feeds">داده‌های این جدول به صورت فایل نیز در دسترس است:
     <a href="/prices.json">prices.json</a> ·
     <a href="/prices.csv">prices.csv</a></p>
</div>
</main>
{footer()}'''


# ------------------------------------------------------------ static pages
def about():
    url = "/about/"
    title = f"درباره {SITE['name_fa']} | فروشگاه قطعات ترمز خودروهای چینی"
    desc = ("عمو چینی، عرضه‌کننده لنت ترمز، دیسک چرخ و کاسه چرخ خودروهای چینی "
            "با تضمین اصالت کالا و مشاوره فنی.")
    cr = [("/", "خانه"), (None, "درباره ما")]
    jsonld = [crumbs_ld(cr), org_ld(),
              {"@context": "https://schema.org", "@type": "AboutPage",
               "name": title, "url": BASE + url, "inLanguage": "fa-IR"}]
    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld)}
{header(url)}
{crumbs(cr)}
<main id="main">
<section class="board-band page-head"><div class="wrap"><h1>درباره {e(SITE["name_fa"])}</h1>
<p>{e(SITE["tagline"])}</p></div></section>
<div class="wrap"><div class="prose">
  <p>عمو چینی روی یک چیز تمرکز دارد: قطعات سیستم ترمز خودروهای چینی که در ایران
  تردد می‌کنند. لنت ترمز، دیسک چرخ و کاسه چرخ — برای ام‌وی‌ام، جک، لیفان، چری،
  هایما، برلیانس، چانگان، جیلی، بست و دیگر برندها.</p>

  <h2>چرا فقط ترمز؟</h2>
  <p>چون قطعه ترمز اشتباه، خطرناک است. تمرکز روی یک سیستم به ما اجازه می‌دهد
  تطابق قطعه با خودرو را دقیق بررسی کنیم و انبار عمیق‌تری از همان چند دسته
  نگه داریم، به‌جای آنکه از هر چیزی کمی داشته باشیم.</p>

  <h2>مشاوره پیش از خرید</h2>
  <p>اگر مطمئن نیستید کدام قطعه به خودروی شما می‌خورد، پیش از سفارش تماس بگیرید.
  مدل، سال ساخت و محور (جلو یا عقب) را بگویید — یا شماره شاسی را بفرستید تا
  تطابق را بررسی کنیم. این کار رایگان است و از یک خرید اشتباه جلوگیری می‌کند.</p>

  <h2>قطعات ASMCO</h2>
  <p>{e(SUPPLIER["claim_fa"])} هستیم. تمام قطعات این فروشگاه — لنت ترمز،
  دیسک چرخ و کاسه چرخ — با برند <bdi>ASMCO</bdi> عرضه می‌شوند.</p>
  <p>در صورت مغایرت، کالا طبق شرایط بازگشت تا
  {to_fa_digits(COMMERCE["return_days"])} روز قابل مرجوع است.</p>

  <h2>سفارش</h2>
  <p>سفارش‌ها تلفنی و از طریق واتساپ ثبت می‌شوند. برای استعلام قیمت روز و
  موجودی، <a href="/contact/">با ما تماس بگیرید</a>.</p>
</div></div>
</main>
{footer()}'''


def contact():
    url = "/contact/"
    title = f"تماس با {SITE['name_fa']} | سفارش و استعلام قیمت"
    desc = (f"تماس با عمو چینی برای استعلام قیمت و سفارش قطعات ترمز خودروهای چینی. "
            f"تلفن، واتساپ و نشانی فروشگاه.")
    cr = [("/", "خانه"), (None, "تماس با ما")]
    wa = SOCIAL.get("whatsapp") or CONTACT["whatsapp"]
    jsonld = [crumbs_ld(cr), org_ld(),
              {"@context": "https://schema.org", "@type": "ContactPage",
               "name": title, "url": BASE + url, "inLanguage": "fa-IR"}]
    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld)}
{header(url)}
{crumbs(cr)}
<main id="main">
<section class="board-band page-head"><div class="wrap"><h1>تماس با ما</h1>
<p>برای استعلام قیمت روز، بررسی موجودی یا مشاوره فنی تماس بگیرید.</p></div></section>
<div class="wrap"><div class="prose">
  <table class="spec">
    <caption>راه‌های ارتباطی</caption>
    <tbody>
      <tr><th scope="row">تلفن</th><td><a href="tel:{e(CONTACT["phone_tel"])}">{bdi(CONTACT["phone_display"])}</a></td></tr>
      <tr><th scope="row">همراه / واتساپ</th><td><a href="tel:{e(CONTACT["mobile_tel"])}">{bdi(CONTACT["mobile_display"])}</a></td></tr>
      <tr><th scope="row">ایمیل</th><td><a href="mailto:{e(CONTACT["email"])}">{bdi(CONTACT["email"])}</a></td></tr>
      <tr><th scope="row">نشانی</th><td>{e(CONTACT["street"])}{("، " + e(CONTACT["city"])) if CONTACT["city"] else ""}<br>
        <a href="{e(CONTACT["map_url"])}" rel="noopener" target="_blank">مشاهده روی نقشه گوگل</a></td></tr>
      <tr><th scope="row">ساعات کاری</th><td>{e(CONTACT["hours_display"])}</td></tr>
    </tbody>
  </table>

  <div class="cta">
    <a class="call" href="tel:{e(CONTACT["phone_tel"])}">تماس تلفنی</a>
    <a class="wa" href="https://wa.me/{e(wa)}" rel="noopener" target="_blank">گفتگو در واتساپ</a>
  </div>

  <h2>پیش از تماس این‌ها را آماده داشته باشید</h2>
  <ul>
    <li>برند و مدل خودرو (مثلاً ام‌وی‌ام ۳۱۵)</li>
    <li>سال ساخت</li>
    <li>محور مورد نظر: جلو یا عقب</li>
    <li>در صورت امکان، کد کالای مورد نظر از سایت</li>
  </ul>
  <p>با این اطلاعات می‌توانیم در همان تماس تطابق قطعه و قیمت نهایی را تأیید کنیم.</p>
</div></div>
</main>
{footer()}'''


def not_found():
    return f'''{head(title="صفحه پیدا نشد | " + SITE["name_fa"],
                     description="صفحه مورد نظر پیدا نشد. از دسته‌بندی لنت ترمز، دیسک چرخ و کاسه چرخ یا جستجوی سایت استفاده کنید.",
                     canonical="/404.html", robots="noindex, follow")}
{header()}
<main id="main"><div class="wrap nf">
  <h1>۴۰۴</h1>
  <h2>این صفحه پیدا نشد</h2>
  <p>ممکن است نشانی تغییر کرده باشد. از دسته‌بندی‌ها شروع کنید یا جستجو کنید.</p>
  <p class="nf-links">
    <a class="btn" href="/">صفحه اصلی</a>
    <a class="btn" href="/brake-pads/">لنت ترمز</a>
    <a class="btn" href="/brake-discs/">دیسک چرخ</a>
    <a class="btn" href="/brands/">خودروها</a>
  </p>
</div></main>
{footer()}'''
