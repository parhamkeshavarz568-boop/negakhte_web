# -*- coding: utf-8 -*-
"""
Every business-specific value the site renders lives here, in one file.

Anything marked  TODO:  is a PLACEHOLDER carried over from the original draft.
It MUST be replaced with the real value before launch — several of them
(phone, address, e-Namad) are load-bearing for local SEO and for Iranian
e-commerce compliance. See docs/PLACEHOLDERS.md.
"""

# ---------------------------------------------------------------- identity
# HTTP or HTTPS?
#   The one URL Google currently has indexed for this domain is  http://amochini.ir/
#   and every product image on the live WordPress site is served over http.
#   .ir domains are genuinely hard to get a certificate for — Sectigo, which is
#   cPanel's default AutoSSL provider, will not issue for .ir; Let's Encrypt will.
#   Publishing https:// canonicals against a domain with no certificate takes the
#   whole site offline for users AND Googlebot, so http is the safe default.
#   FLIP THIS TO "https" ONLY AFTER someone outside Iran confirms:
#       curl -I https://amochini.ir/     ->  200, valid chain
#   and uncomment the matching block at the bottom of build/templates/htaccess.tpl.
SCHEME = "http"

SITE = dict(
    domain="amochini.ir",
    base_url=f"{SCHEME}://amochini.ir",    # no trailing slash
    scheme=SCHEME,
    # The business is عمو چینی ("Uncle Chinese"), which is what amochini spells
    # out. The uploaded draft was branded یدک‌رسان — a different company name
    # entirely, carried over from whatever template it started life as.
    name_fa="عمو چینی",
    name_en="Amochini",
    # The <title> suffix. Kept short: Persian is compact and titles are
    # truncated on PIXEL width, not character count.
    brand_suffix="عمو چینی",
    tagline="فروشگاه قطعات ترمز خودروهای چینی",
    # The slogan the live site already uses.
    slogan="با عمو چینی همه قطعات پیدا میشه",
    description=(
        "خرید لنت ترمز، دیسک چرخ و کاسه چرخ خودروهای چینی با قیمت روز. "
        "ام‌وی‌ام، جک، لیفان، چری، هایما، برلیانس، چانگان، جیلی و بست."
    ),
    lang="fa",            # W3C: shortest subtag that captures the distinction
    locale="fa_IR",
    theme_color="#fbb316",
)

# ---------------------------------------------------------------- contact
# TODO: every value in this block is a placeholder from the draft.
CONTACT = dict(
    # 09122650076 is the number the live amochini.ir publishes — it appears in
    # Google's cached description of the site. VERIFY it is still current before
    # launch; it is taken from the search index, not from the owner directly.
    phone_display="۰۹۱۲۲۶۵۰۰۷۶",
    phone_tel="+989122650076",
    mobile_display="۰۹۱۲۲۶۵۰۰۷۶",
    mobile_tel="+989122650076",
    whatsapp="989122650076",                # digits only, no +
    email="info@amochini.ir",               # TODO: confirm this mailbox exists
    street="نشانی نمونه، خیابان نمونه، پلاک ۰۰",   # TODO: real street address
    city="تهران",                            # TODO: confirm city
    region="تهران",                          # TODO: confirm province
    postal_code="",                          # TODO: real postcode (helps local SEO)
    country="IR",
    hours_display="شنبه تا پنج‌شنبه، ۸ الی ۱۷",
    # schema.org openingHours — 24h, Gregorian day codes
    hours_schema=["Sa 08:00-17:00", "Su 08:00-17:00", "Mo 08:00-17:00",
                  "Tu 08:00-17:00", "We 08:00-17:00", "Th 08:00-17:00"],
    # TODO: real coordinates of the shop. Leave as None to omit geo from schema
    # rather than publish wrong ones — a wrong pin is worse than no pin.
    latitude=None,
    longitude=None,
)

# ---------------------------------------------------------------- socials
# The draft linked Facebook, Twitter and Google+. Google+ shut down in 2019 and
# Facebook/Twitter are filtered in Iran — all three were dead links. These are
# the channels Iranian shoppers actually use.
# TODO: fill in the real handles; any left empty is simply not rendered.
SOCIAL = dict(
    instagram="",      # TODO e.g. "amochini"
    telegram="",       # TODO e.g. "amochini"
    whatsapp="",       # TODO digits only; falls back to CONTACT["whatsapp"]
    eitaa="",          # TODO optional
)

# ---------------------------------------------------------------- supplier
# The part manufacturer. Confirmed by the owner: all 130 SKUs are ASMCO, and
# the business supplies ASMCO parts in Iran.
#
# This is the correct value for schema.org `brand` on a Product — the
# catalogue's own "brand" field is the CAR the part fits, which is a different
# thing entirely. TRA-X and XTRA are ASMCO product LINES, so they are emitted
# as a product series property rather than as brands.
#
# The wording below is the conservative form the owner chose. Stronger claims
# ("توزیع‌کننده اصلی", "نماینده رسمی") are legal assertions about an agency
# relationship — change this only to wording the business can actually stand
# behind, since it renders on all 153 pages.
SUPPLIER = dict(
    part_brand="ASMCO",
    part_brand_fa="ASMCO",
    claim_fa="عرضه‌کننده قطعات ASMCO",
    tagline_fa="قطعات ترمز ASMCO — تضمین اصالت کالا",
)

# ---------------------------------------------------------------- commerce
COMMERCE = dict(
    # The source data stores prices in RIAL (the cart in the draft read "۰ ریال",
    # and the values only make sense as Rial: 25,987,500 IRR = 2,598,750 Toman
    # for a brake drum is plausible; 25.9M Toman is not).
    # Iranians shop in TOMAN, so Toman is what we show. Schema.org requires an
    # ISO 4217 code and Toman has none, so JSON-LD emits IRR with the Rial value.
    stored_currency="IRR",
    display_unit="تومان",
    display_divisor=10,               # Rial -> Toman
    # TODO: confirm with the owner. If the source numbers are actually Toman,
    # set display_divisor=1 and stored_currency stays IRR with price*10.
    price_valid_days=7,               # priceValidUntil horizon for Offer
    # There is no cart or checkout on this site. Orders are taken by phone and
    # WhatsApp, which is normal for Iranian parts retail. Setting this to False
    # keeps the fake "add to cart" button out of the build.
    online_checkout=False,
    free_shipping_over_toman=10_000_000,   # TODO: confirm threshold
    return_days=7,                          # TODO: confirm returns policy
)

# ---------------------------------------------------------------- trust
# Iranian online shops are legally expected to display اینماد (e-Namad) and
# ساماندهی. These are per-site codes issued to the business.
# TODO: paste the real badge codes/HTML. Empty = a labelled placeholder slot
# renders instead, so the layout is already correct when you add them.
TRUST = dict(
    enamad_code="",      # TODO e-Namad
    samandehi_code="",   # TODO ساماندهی
)

# ---------------------------------------------------------------- analytics
# TODO: pick one and paste the snippet. Left empty, nothing is injected —
# the site ships with zero third-party requests, which is the right default
# for in-Iran page speed.
ANALYTICS = dict(head_html="", body_end_html="")
