# -*- coding: utf-8 -*-
"""
Every business-specific value the site renders lives here, in one file.

Anything marked  TODO:  is a PLACEHOLDER carried over from the original draft.
It MUST be replaced with the real value before launch — several of them
(phone, address, e-Namad) are load-bearing for local SEO and for Iranian
e-commerce compliance. See docs/PLACEHOLDERS.md.
"""

# ---------------------------------------------------------------- identity
SITE = dict(
    domain="amochini.ir",
    base_url="https://amochini.ir",        # https, no trailing slash
    name_fa="آموچینی",
    name_en="Amochini",
    # The <title> suffix. Kept short: Persian is compact and titles are
    # truncated on PIXEL width, not character count.
    brand_suffix="آموچینی",
    tagline="فروشگاه قطعات ترمز خودروهای چینی",
    description=(
        "خرید لنت ترمز، دیسک چرخ و کاسه چرخ خودروهای چینی با قیمت روز. "
        "ام‌وی‌ام، جک، لیفان، چری، هایما، برلیانس، چانگان، جیلی و بست."
    ),
    lang="fa-IR",
    locale="fa_IR",
    theme_color="#fbb316",
)

# ---------------------------------------------------------------- contact
# TODO: every value in this block is a placeholder from the draft.
CONTACT = dict(
    phone_display="۰۲۱–۱۲۳۴۵۶۷۸",          # TODO: real number, Persian digits
    phone_tel="+982112345678",              # TODO: real number, E.164 for tel:
    mobile_display="۰۹۱۲–۱۲۳۴۵۶۷",          # TODO: real mobile
    mobile_tel="+989121234567",             # TODO: E.164
    whatsapp="989121234567",                # TODO: digits only, no +
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
