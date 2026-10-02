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

    # The shop sells whatever customers ask for, not only handmade pieces, so
    # nothing on the site positions it as a handmade store.
    # The tagline is plain description: page titles, the footer, link previews.
    "tagline": "شمع، سفال، نقره، عطر و هدیه؛ و هر چیزی که دنبالش باشی",
    "description": ("شمع، سفال، گل بافتنی، نقره، عطر و هدیه؛ و هر چیزی که دنبالش باشی. "
                    "هر قطعه یه کد داره؛ کدش رو بفرست تا هماهنگ کنیم."),

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

# The home page headline: one of these verses, chosen at random on every load
# (never the same one twice in a row), one line per misra, the poet named
# beneath, and `em` set in oxblood on the gold highlighter. The first is the
# default, shown when JavaScript is off.
#
# Every verse is checked against Ganjoor (ganjoor.net) and given in its exact
# text, with the poem it comes from as `source`; validate.py refuses a verse
# without one. Do not add a verse from memory: three of the first candidates
# were misremembered (انیس ← رفیق، نکته ← قصه، در نظر هوشیار ← پیش خداوند هوش)
# and one was only *attributed* to Hafez. All are public domain.
HERO = [
    {"poet": "خیام", "em": "دو هزار کوزه",
     "poem": ["در کارگه کوزه‌گری رفتم دوش",
              "دیدم دو هزار کوزه گویا و خموش"],
     "source": "https://ganjoor.net/khayyam/robaee/sh117"},
    {"poet": "حافظ", "em": "خانه، خانهٔ توست",
     "poem": ["رَواقِ منظرِ چشمِ من آشیانهٔ توست",
              "کَرَم نما و فرود آ که خانه، خانهٔ توست"],
     "source": "https://ganjoor.net/hafez/ghazal/sh34"},
    {"poet": "مولانا", "em": "با چراغ",
     "poem": ["دی شیخ با چراغ همی گشت گِرد شهر",
              "کز دیو و دَد ملولم و انسانم آرزوست"],
     "source": "https://ganjoor.net/moulavi/shams/ghazalsh/sh441"},
    {"poet": "رودکی", "em": "بویِ جویِ مولیان",
     "poem": ["بویِ جویِ مولیان آیَد هَمی",
              "یادِ یارِ مهربان آیَد هَمی"],
     "source": "https://ganjoor.net/roodaki/baghimande/sh121"},
    {"poet": "حافظ", "em": "طرحی نو",
     "poem": ["بیا تا گل برافشانیم و می در ساغر اندازیم",
              "فلک را سقف بشکافیم و طرحی نو دراندازیم"],
     "source": "https://ganjoor.net/hafez/ghazal/sh374"},
    {"poet": "خیام", "em": "این کوزه",
     "poem": ["این کوزه چو من عاشق زاری بوده‌ است",
              "در بندِ سرِ زلفِ نگاری بوده‌ است"],
     "source": "https://ganjoor.net/khayyam/tarane/tkh5/sh16"},
    {"poet": "سعدی", "em": "همه عالم",
     "poem": ["به جهان خُرَّم از آنم که جهان خُرَّم از اوست",
              "عاشقم بر همه عالم که همه عالم از اوست"],
     "source": "https://ganjoor.net/saadi/mavaez/ghazal2/sh13"},
    {"poet": "مولانا", "em": "شمع و شکَر",
     "poem": ["من غلام قمرم، غیر قمر هیچ مگو",
              "پیش من جز سخن شمع و شکَر هیچ مگو"],
     "source": "https://ganjoor.net/moulavi/shams/ghazalsh/sh2219"},
    {"poet": "حافظ", "em": "ستاره‌ای",
     "poem": ["ستاره‌ای بدرخشید و ماهِ مجلس شد",
              "دل رمیدهٔ ما را رفیق و مونس شد"],
     "source": "https://ganjoor.net/hafez/ghazal/sh167"},
    {"poet": "خیام", "em": "یک دمِ عمر",
     "poem": ["ای دوست بیا تا غمِ فردا نخوریم",
              "وین یک دمِ عمر را غنیمت شمریم"],
     "source": "https://ganjoor.net/khayyam/robaee/sh121"},
    {"poet": "سعدی", "em": "برگ درختان سبز",
     "poem": ["برگ درختان سبز، پیش خداوند هوش",
              "هر ورقی دفتری‌ست، معرفت کردگار"],
     "source": "https://ganjoor.net/saadi/divan/ghazals/sh296"},
    {"poet": "مولانا", "em": "این خانه",
     "poem": ["این خانه که پیوسته در او بانگ چغانه‌ست",
              "از خواجه بپرسید که این خانه چه خانه‌ست"],
     "source": "https://ganjoor.net/moulavi/shams/ghazalsh/sh332"},
    {"poet": "حافظ", "em": "پرتوِ حُسنت",
     "poem": ["در ازل پرتوِ حُسنت ز تجلی دَم زد",
              "عشق پیدا شد و آتش به همه عالم زد"],
     "source": "https://ganjoor.net/hafez/ghazal/sh152"},
    {"poet": "خیام", "em": "دریاب دمی",
     "poem": ["این قافلهٔ عمر عجب می‌گذرد",
              "دریاب دمی که با طرب می‌گذرد"],
     "source": "https://ganjoor.net/khayyam/robaee/sh66"},
    {"poet": "حافظ", "em": "فیضِ گل",
     "poem": ["بلبل از فیضِ گل آموخت سخن، ور نه نبود",
              "این همه قول و غزل تعبیه در منقارش"],
     "source": "https://ganjoor.net/hafez/ghazal/sh277"},
]

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

