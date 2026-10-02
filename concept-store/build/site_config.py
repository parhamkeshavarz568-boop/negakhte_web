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
    "tagline_em": "دست‌ساز",      # the word the home page sets in gold
    "description": ("شمع دست‌ساز، سفال، گل بافتنی، نقره، آرایشی و هدیه‌های کوچک. "
                    "هر قطعه یک کد دارد؛ کد را بفرستید تا هماهنگ کنیم."),

    # The domain, e.g. "https://example.ir" — no trailing slash, no folder.
    # None = not decided yet: canonical / og:url / sitemap.xml are left out
    # rather than pointed at a guess.
    "url": None,
    # The folder the site lives in on that domain. "/" when public/ is the web
    # root; "/shop/" if it is uploaded into a folder called shop. Every link,
    # image and the 404 rule follow this one value.
    "base": "/",
    # False = preview: every page says noindex, so an upload made before the
    # name and contacts are final cannot end up in Google under a placeholder.
    # Set True on launch day; validate.py lists it until then.
    "launch": False,
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

# Pieces on the home page's shelf, in order, by code. Positions 1 and 8 are
# the big ones (the magazine rhythm). The build fails if any is missing or
# sold, so a sale never leaves a hole on the home page.
HOME = {
    "shelf": ["C-08", "S-10", "O-26", "B-19", "O-09", "S-23", "O-03", "C-04", "C-20", "O-21"],
}

# The photo for each section's pane in the home page vitrine, by code.
COVERS = {
    "candles": "C-07",
    "ceramics": "S-26",
    "knitted-flowers": "O-61",
    "silver": "O-21",
    "beauty": "B-02",
    "small-gifts": "O-34",
    "incense": "O-13",
    "spices": "O-38",
}

# The mood image at the top of each section page (build/original/atmosphere/).
# The four material studies go to their own sections; the rest share the
# empty sunlit corner.
BANNERS = {
    "candles": "candles",
    "ceramics": "ceramics",
    "knitted-flowers": "crochet",
    "silver": "silver",
    "beauty": "hero-wide",
    "small-gifts": "hero-tall",
    "incense": "light-ledge",
    "spices": "hero-wide",
}

# Sections whose pieces are made by hand, one at a time. Their product pages
# say so, and that the piece may differ slightly from the photo.
HANDMADE = {"candles", "ceramics", "knitted-flowers"}
