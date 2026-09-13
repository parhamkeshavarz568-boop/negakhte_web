# -*- coding: utf-8 -*-
"""Page bodies. Each function returns a full HTML document."""
from normalize import to_fa_digits, BRANDS, CATEGORIES, VARIANTS, AXLES
from site_config import SITE, CONTACT, COMMERCE, SOCIAL
from layout import (e, ld, money, bdi, head, header, footer, crumbs, crumbs_ld,
                    BASE, sameas, SVG)
import json as _json, os as _os

# Which widths actually exist on disk for each image, written by build.py.
# Templates ask for a size and get the closest one that exists, so a
# 400px-only source is never requested at 700px (which would 404).
_IMG = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                     "data", "images.json"), encoding="utf-8"))


def img_w(name, want):
    """Largest available width <= want, else the smallest available."""
    sizes = _IMG.get(name)
    if not sizes:
        return want
    ok = [s for s in sizes if s <= want]
    return max(ok) if ok else min(sizes)

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
        # NOTE: `brand` is deliberately NOT the car make. The `b` field in the
        # source data is the vehicle it fits (ام‌وی‌ام, جک...), not who
        # manufactured the part. Emitting "brand": "MVM" on a brake disc
        # asserts MVM made it, which is false and is exactly the misleading
        # markup that earns a structured-data manual action. The car make is
        # expressed through isAccessoryOrSparePartFor instead.
        # TRA-X / XTRA *are* genuine product lines, so those get a brand.
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
    if p["variant"] != "base":
        node["brand"] = {"@type": "Brand", "name": VARIANTS[p["variant"]]["code"]}
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
    if p["price_irr"] is None:
        return ('<div class="price-na">قیمت: تماس بگیرید</div>' if big
                else '<div class="price na">استعلام قیمت</div>')
    toman = money(p["price_irr"], data=True)
    rial = to_fa_digits(f"{p['price_irr']:,}").replace(",", "،")
    if big:
        return (f'<div class="price-main">{toman}</div>'
                f'<div class="price-alt">معادل {rial} ریال</div>')
    return f'<div class="price">{toman}</div>'


def card(p):
    b = BRANDS[p["brand"]]
    badge = ""
    if not p["in_stock"]:
        badge = '<span class="badge">ناموجود</span>'
    elif p["variant"] != "base":
        badge = f'<span class="badge v">{e(VARIANTS[p["variant"]]["code"])}</span>'
    img = p["image"]
    cta = ('<a class="add" href="{}">مشاهده و سفارش</a>'.format(e(p["url"]))
           if p["price_irr"] is not None else
           '<a class="add na" href="{}">استعلام قیمت</a>'.format(e(p["url"])))
    return f'''<article class="card" data-brand="{e(p["brand"])}" data-axle="{e(p["axle"])}"
         data-price="{p["price_irr"] if p["price_irr"] is not None else ""}"
         data-title="{e(p["title"])}" data-search="{e(p["search"])}">
  <div class="ph">{badge}
    <picture>
      <source type="image/webp" srcset="/assets/img/{img}-400.webp">
      <img src="/assets/img/{img}-400.jpg" alt="{e(p["title"])}"
           width="400" height="400" loading="lazy" decoding="async">
    </picture>
  </div>
  <div class="body">
    <h3><a href="{e(p["url"])}">{e(p["title"])}</a></h3>
    <p class="sku">کد کالا: {bdi(p["sku"])}</p>
    <div class="tags">
      <span class="brand">{e(b["fa"])}</span>
      <span>{e(AXLE_FA[p["axle"]])}</span>
    </div>
    {price_block(p)}
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
        ("دسته‌بندی", cat["fa"]),
        ("خودرو", f"{b['fa']}{model}".strip()),
        ("محور", axle),
        ("مدل محصول", v["fa"]),
        ("کد کالا", p["sku"]),
    ]
    spec = "".join(f"<tr><th scope=\"row\">{e(k)}</th><td>{bdi(val) if k=='کد کالا' else e(val)}</td></tr>"
                   for k, val in spec_rows)

    rel = related(p, all_p)
    rel_html = "".join(card(x) for x in rel)

    big = img_w(p["image"], 700)
    small = img_w(p["image"], 400)
    parts = sorted({small, big})
    srcset_w = ", ".join(f"/assets/img/{p['image']}-{w}.webp {w}w" for w in parts)

    jsonld = [product_ld(p), crumbs_ld(cr), faq_ld(qa), org_ld()]

    return f'''{head(title=title, description=desc, canonical=p["url"],
                     jsonld=jsonld, og_type="product",
                     og_image=f"/assets/img/{p['image']}-{img_w(p['image'],700)}.jpg")}
{header()}
{crumbs(cr)}
<main id="main">
<div class="wrap">
  <div class="product">
    <div class="gallery">
      <picture>
        <source type="image/webp" srcset="{srcset_w}">
        <img src="/assets/img/{p['image']}-{big}.jpg" alt="{e(p['title'])}"
             width="{big}" height="{big}" fetchpriority="high" decoding="async">
      </picture>
    </div>

    <div class="info">
      <h1>{e(p["title"])}</h1>
      <p class="sub">کد کالا: {bdi(p["sku"])} — {e(v["fa"])}</p>

      <div class="price-box">
        {price_block(p, big=True)}
        <div class="stock{stock_cls}">{e(stock_txt)}</div>
      </div>

      <div class="cta">
        <a class="call" href="tel:{e(CONTACT["phone_tel"])}">تماس و سفارش: {bdi(CONTACT["phone_display"])}</a>
        <a class="wa" href="https://wa.me/{e(wa)}?text={e("سلام، درباره " + p["title"] + " (" + p["sku"] + ") سوال داشتم.")}"
           rel="noopener" target="_blank">سفارش در واتساپ</a>
      </div>

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

<div class="wrap related">
  <h2>قطعات مرتبط برای {e(b["fa"])}{e(model)}</h2>
  <div class="grid-products">{rel_html}</div>
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
<div class="page-head"><div class="wrap">
  <h1>{e(c["h1"])}</h1>
  <p>{e(c["blurb"])} — {e(brand_names)} و دیگر خودروهای چینی.</p>
  <p class="meta">{to_fa_digits(n)} کالا در این دسته{(" — " + rng) if rng else ""}</p>
</div></div>

<div class="wrap shop">
  <h2 class="sr-only">فهرست محصولات</h2>
  {filter_bar(prods, brands_present)}
  <div class="grid-products" id="grid">{"".join(card(p) for p in prods)}</div>
  <p class="empty" id="empty" hidden>کالایی با این مشخصات پیدا نشد. فیلترها را تغییر دهید یا با ما تماس بگیرید.</p>
</div>

<div class="wrap">
  {faq_block(qa)}
  <section class="faq">
    <h2>{e(c["fa"])} بر اساس خودرو</h2>
    <p class="brandlinks" style="display:flex;flex-wrap:wrap;gap:10px;padding-top:6px">{brand_links}</p>
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
        sections += (f'<h2 class="section-title"><b>{e(CATEGORIES[c]["fa"])}</b> '
                     f'{e(b["fa"])}</h2>'
                     f'<div class="grid-products">{"".join(card(p) for p in items)}</div>'
                     f'<p style="text-align:center;margin:18px 0 34px">'
                     f'<a href="/{e(c)}/" style="color:var(--gold-ink);font-weight:500">'
                     f'مشاهده همه {e(CATEGORIES[c]["fa"])} ›</a></p>')

    model_list = ("".join(f"<li>{e(m)}</li>" for m in models)) or "<li>—</li>"
    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld)}
{header("/brands/")}
{crumbs(cr)}
<main id="main">
<div class="page-head"><div class="wrap">
  <h1>قطعات ترمز {e(b["fa"])}</h1>
  <p>{e(cats_fa)} برای خودروهای {e(b["fa"])}{(" — مدل‌های " + e(models_fa)) if models_fa else ""}.</p>
  <p class="meta">{to_fa_digits(n)} کالا</p>
</div></div>

<div class="wrap shop">{sections}</div>

<div class="wrap">
  <section class="faq">
    <h2>مدل‌های {e(b["fa"])} که قطعه آن‌ها را داریم</h2>
    <ul style="columns:2;padding-inline-start:20px;padding-top:8px">{model_list}</ul>
  </section>
  {faq_block(qa)}
</div>
</main>
{footer()}'''


def brands_index(groups):
    url = "/brands/"
    title = f"قطعات ترمز بر اساس خودرو | {SITE['brand_suffix']}"
    desc = ("انتخاب لنت ترمز، دیسک چرخ و کاسه چرخ بر اساس برند خودرو: "
            + "، ".join(BRANDS[s]["fa"] for s in list(groups)[:10]) + " و بیشتر.")
    cr = [("/", "خانه"), (None, "خودروها")]
    cards = "".join(
        f'<a href="/brands/{e(s)}/">{e(BRANDS[s]["fa"])}'
        f'<small>{to_fa_digits(len(v))} کالا</small></a>'
        for s, v in sorted(groups.items(), key=lambda kv: -len(kv[1])))
    jsonld = [crumbs_ld(cr), org_ld(),
              {"@context": "https://schema.org", "@type": "CollectionPage",
               "name": title, "url": BASE + url, "inLanguage": "fa-IR"}]
    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld)}
{header(url)}
{crumbs(cr)}
<main id="main">
<div class="page-head"><div class="wrap">
  <h1>قطعات ترمز بر اساس خودرو</h1>
  <p>خودروی خود را انتخاب کنید تا لنت ترمز، دیسک چرخ و کاسه چرخ مناسب آن را ببینید.</p>
</div></div>
<div class="wrap" style="padding-top:26px">
  <h2 class="sr-only">فهرست برندهای خودرو</h2>
  <div class="brandgrid">{cards}</div>
</div>
</main>
{footer()}'''


# --------------------------------------------------------------------- home
def home(all_p, groups):
    url = "/"
    title = f"{SITE['name_fa']} | لنت ترمز، دیسک و کاسه چرخ خودروهای چینی"
    desc = SITE["description"]
    cr = [(None, "خانه")]

    counts = {c: sum(1 for p in all_p if p["category"] == c) for c in CAT_ORDER}
    cat_imgs = {"brake-pads": "cat-brake-pads", "brake-discs": "cat-brake-discs",
                "brake-drums": "cat-headlight"}
    cats_html = ""
    for c in CAT_ORDER:
        cc = CATEGORIES[c]
        cats_html += f'''<article class="cat">
      <div>
        <h3><a href="/{e(c)}/">{e(cc["fa"])}</a></h3>
        <p class="cat-count">{to_fa_digits(counts[c])} کالا</p>
        <a href="/{e(c)}/" class="all">نمایش همه ›</a>
      </div>
      <div class="thumb">
        <picture>
          <source type="image/webp" srcset="/assets/img/{cat_imgs[c]}-400.webp">
          <img src="/assets/img/{cat_imgs[c]}-400.jpg" alt="{e(cc["fa"])}"
               width="400" height="400" loading="lazy" decoding="async">
        </picture>
      </div>
    </article>'''

    # Vehicle finder — real options built from the catalogue, wired to real URLs.
    brand_opts = "".join(
        f'<option value="{e(s)}">{e(BRANDS[s]["fa"])}</option>'
        for s in sorted(groups, key=lambda s: BRANDS[s]["fa"]))
    cat_opts = "".join(f'<option value="{e(c)}">{e(CATEGORIES[c]["fa"])}</option>'
                       for c in CAT_ORDER)

    featured = [p for p in all_p if p["in_stock"]][:8]
    qa = [
        ("چطور قطعه مناسب خودروی چینی‌ام را پیدا کنم؟",
         "از جستجوگر بالای صفحه، برند خودرو و نوع قطعه را انتخاب کنید. اگر مدل "
         "دقیق را نمی‌دانید، کارت خودرو یا شماره شاسی را برای ما بفرستید."),
        ("قیمت‌ها به‌روز هستند؟",
         "قیمت‌های درج‌شده قیمت روز است، اما بازار قطعات نوسان دارد. پیش از "
         "سفارش، قیمت نهایی را تلفنی یا در واتساپ تأیید کنید."),
        ("ارسال به شهرستان دارید؟",
         "بله، ارسال به سراسر ایران انجام می‌شود."),
        ("قطعات اصلی هستند یا طرح؟",
         "کالاها با تضمین اصالت عرضه می‌شوند و در صورت مغایرت قابل مرجوع هستند."),
    ]
    jsonld = [org_ld(), website_ld(), faq_ld(qa),
              itemlist_ld(featured, "پرفروش‌ترین قطعات ترمز", "/")]

    return f'''{head(title=title, description=desc, canonical=url, jsonld=jsonld,
                     preload_hero=True)}
{header("/")}
<main id="main">
<section class="hero">
  <div class="art">
    <picture>
      <source type="image/webp"
              srcset="/assets/img/hero-bg-640.webp 640w, /assets/img/hero-bg-1024.webp 1024w, /assets/img/hero-bg-1500.webp 1500w"
              sizes="100vw">
      <img src="/assets/img/hero-bg-1024.jpg" alt="" width="1500" height="844"
           fetchpriority="high" decoding="async">
    </picture>
  </div>
  <div class="inner">
    <h1>قطعات ترمز خودروهای چینی، با قیمت روز</h1>
    <p>{e(SITE["slogan"])} — {to_fa_digits(len(all_p))} کالا برای {to_fa_digits(len(groups))} برند</p>

    <form class="finder" id="finder" action="/brake-pads/" method="get">
      <label class="sr-only" for="f-brand">خودرو</label>
      <select id="f-brand" name="brand"><option value="">خودرو را انتخاب کنید</option>{brand_opts}</select>
      <label class="sr-only" for="f-cat">نوع قطعه</label>
      <select id="f-cat" name="cat"><option value="">نوع قطعه</option>{cat_opts}</select>
      <label class="sr-only" for="f-axle">محور</label>
      <select id="f-axle" name="axle"><option value="">محور</option><option value="front">جلو</option><option value="rear">عقب</option></select>
      <button type="submit">جستجوی قطعه</button>
    </form>
  </div>
</section>

<div class="wrap">
  <h2 class="section-title"><b>دسته‌بندی</b>‌های محصولات</h2>
  <section class="cats">{cats_html}</section>
</div>

<div class="wrap shop">
  <h2 class="section-title"><b>پرفروش‌ترین</b> قطعات</h2>
  <div class="grid-products">{"".join(card(p) for p in featured)}</div>
  <p style="text-align:center;margin-top:26px">
    <a class="more-btn" href="/brake-discs/">مشاهده همه محصولات</a>
  </p>
</div>

<div class="wrap">
  <h2 class="section-title"><b>خرید</b> بر اساس خودرو</h2>
  <div class="brandgrid">{"".join(f'<a href="/brands/{e(s)}/">{e(BRANDS[s]["fa"])}<small>{to_fa_digits(len(v))} کالا</small></a>' for s, v in sorted(groups.items(), key=lambda kv: -len(kv[1])))}</div>
  {faq_block(qa)}
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
<div class="page-head"><div class="wrap"><h1>درباره {e(SITE["name_fa"])}</h1>
<p>{e(SITE["tagline"])}</p></div></div>
<div class="wrap"><div class="prose" style="background:#fff;padding:26px;margin-block:26px;max-width:none">
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

  <h2>اصالت کالا</h2>
  <p>کالاها با تضمین اصالت عرضه می‌شوند. در صورت مغایرت، کالا طبق شرایط بازگشت
  تا {to_fa_digits(COMMERCE["return_days"])} روز قابل مرجوع است.</p>

  <h2>سفارش</h2>
  <p>سفارش‌ها تلفنی و از طریق واتساپ ثبت می‌شوند. برای استعلام قیمت روز و
  موجودی، <a href="/contact/" style="color:var(--gold-ink)">با ما تماس بگیرید</a>.</p>
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
<div class="page-head"><div class="wrap"><h1>تماس با ما</h1>
<p>برای استعلام قیمت روز، بررسی موجودی یا مشاوره فنی تماس بگیرید.</p></div></div>
<div class="wrap"><div class="prose" style="background:#fff;padding:26px;margin-block:26px;max-width:none">
  <table class="spec" style="margin-top:0">
    <caption>راه‌های ارتباطی</caption>
    <tbody>
      <tr><th scope="row">تلفن</th><td><a href="tel:{e(CONTACT["phone_tel"])}">{bdi(CONTACT["phone_display"])}</a></td></tr>
      <tr><th scope="row">همراه / واتساپ</th><td><a href="tel:{e(CONTACT["mobile_tel"])}">{bdi(CONTACT["mobile_display"])}</a></td></tr>
      <tr><th scope="row">ایمیل</th><td><a href="mailto:{e(CONTACT["email"])}">{bdi(CONTACT["email"])}</a></td></tr>
      <tr><th scope="row">نشانی</th><td>{e(CONTACT["street"])}{("، " + e(CONTACT["city"])) if CONTACT["city"] else ""}</td></tr>
      <tr><th scope="row">ساعات کاری</th><td>{e(CONTACT["hours_display"])}</td></tr>
    </tbody>
  </table>

  <div class="cta" style="display:flex;gap:10px;flex-wrap:wrap;margin-top:24px">
    <a class="call" style="background:var(--yellow);color:#1a1a1a;padding:14px 26px;font-weight:500;flex:1 1 200px;text-align:center"
       href="tel:{e(CONTACT["phone_tel"])}">تماس تلفنی</a>
    <a class="wa" style="background:#1f1f1f;color:#fff;padding:14px 26px;font-weight:500;flex:1 1 200px;text-align:center"
       href="https://wa.me/{e(wa)}" rel="noopener" target="_blank">گفتگو در واتساپ</a>
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
  <p style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
    <a class="btn" href="/">صفحه اصلی</a>
    <a class="btn" href="/brake-pads/">لنت ترمز</a>
    <a class="btn" href="/brake-discs/">دیسک چرخ</a>
    <a class="btn" href="/brands/">خودروها</a>
  </p>
</div></main>
{footer()}'''
