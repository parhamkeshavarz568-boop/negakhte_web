# -*- coding: utf-8 -*-
"""
Every business-specific value, in one file. Change a value, run build.py.

Values set to None are not known yet. The build never invents them: a missing
channel renders no link, a missing domain emits no canonical or sitemap, and
validate.py lists every one as a launch blocker until it is filled in.
"""

SITE = {
    # PLACEHOLDER — the shop's real name was not in the export. «کانسپت استور» is
    # what the owner's folder was called; swap both lines for the real name.
    "name_fa": "کانسپت استور",
    "name_en": "Concept Store",
    "name_is_placeholder": True,

    "tagline": "چیزهای کوچکِ دست‌ساز، یکی‌یکی انتخاب‌شده",
    "description": ("شمع دست‌ساز، سفال، گل بافتنی، نقره، آرایشی و هدیه‌های کوچک. "
                    "هر قطعه یک کد دارد؛ کد را بفرستید تا هماهنگ کنیم."),

    # e.g. "https://example.ir" — no trailing slash. None = not decided yet:
    # canonical / og:url / sitemap.xml are left out rather than pointed at a guess.
    "url": None,
    "locale": "fa_IR",
}

# Ordering is by message: the visitor sends a piece's code. Fill in the
# channels the shop actually answers on; the others simply do not appear.
CONTACT = {
    "instagram": None,     # handle without @, e.g. "shopname" -> ig.me/m/shopname opens the DM
    "telegram": None,      # username without @
    "whatsapp": None,      # international, digits only, e.g. "989121234567"
    "phone": None,         # as dialled, e.g. "+989121234567"
    "phone_display": None, # as printed, e.g. "۰۹۱۲ ۱۲۳ ۴۵۶۷"
    "address": None,       # street address, if there is a shop to visit
    "hours": None,         # e.g. "هر روز ۱۱ تا ۲۱"
    "city": None,
}

# Pieces chosen for the front of the shop, by code. The build fails if any of
# these is missing or sold, so a sale never leaves a hole on the home page.
HOME = {
    "hero": ["C-08", "S-26", "O-61"],
    "shelf": ["C-04", "S-10", "O-26", "B-19", "O-21", "S-23", "C-20", "O-03"],
}

# The cover photo of each section on the home page.
COVERS = {
    "candles": "C-07",
    "ceramics": "S-26",
    "knitted-flowers": "O-61",
    "silver": "O-21",
    "beauty": "B-19",
    "small-gifts": "O-34",
    "incense": "O-03",
    "spices": "O-38",
}

# Sections whose pieces are made by hand, one at a time. Their product pages
# say so, and that the piece may differ slightly from the photo.
HANDMADE = {"candles", "ceramics", "knitted-flowers"}
