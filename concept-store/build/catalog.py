# -*- coding: utf-8 -*-
"""
Everything the site knows about the catalogue's *shape*: the owner's four
lists, the eight sections a visitor browses, and the rules that turn a
spreadsheet cell into a product name.

The owner's lists are organised by supplier (Candle, SOFAL, Nixgel/Niura, and
"Other"). That is the right shape for the owner and the wrong one for a
shopper: "Other" holds silver, incense, crochet flowers, spices, postcards and
figurines. So the three supplier lists map one-to-one to a section, and "Other"
is split by what each item *is* (classify()).
"""
import re

# The owner's lists. `prefix` starts every product code from that list, and a
# code never changes once published — customers quote it in messages.
COLLECTIONS = {
    "candle":  {"prefix": "C", "list": "Candle"},
    "beauty":  {"prefix": "B", "list": "Nixgel - Atr - Niura"},
    "other":   {"prefix": "O", "list": "Other"},
    "ceramic": {"prefix": "S", "list": "SOFAL"},
}

# The sections of the site, in the order the home page shows them.
# `intro` is section copy: it says only what the photos and the owner's lists
# establish. Edit freely — it is marked for review in docs/REVIEW-FA.md.
CATEGORIES = [
    {"slug": "candles", "fa": "شمع", "en": "Candles",
     "intro": "شمع‌های آیشید؛ کیکی، میوه‌ای، ماه و استوانه‌های نقاشی‌شده."},
    {"slug": "ceramics", "fa": "سفال", "en": "Ceramics",
     "intro": "ماگ، کاسه، دیس و گلدانِ سفالیِ لعاب‌دار."},
    {"slug": "knitted-flowers", "fa": "گل‌های بافتنی", "en": "Crochet flowers",
     "intro": "رز، آفتابگردان و لیلیوم بافتنی؛ گلی که پژمرده نمی‌شود."},
    {"slug": "silver", "fa": "نقره", "en": "Silver",
     "intro": "دستبند، آویز، انگشتر و گوشوارهٔ نقره. قیمت هر قطعه به نرخ روز نقره اعلام می‌شود."},
    {"slug": "beauty", "fa": "آرایش و مراقبت", "en": "Beauty & care",
     "intro": "آرایشیِ نیکس‌ژل، مراقبتِ بدنِ نیورا و عطرِ الورا."},
    {"slug": "small-gifts", "fa": "هدیه‌های کوچک", "en": "Small gifts",
     "intro": "استیکرهای برجسته، کارت پستال و پین؛ برای وقتی که یک چیز کوچک کافی است."},
    {"slug": "incense", "fa": "عود", "en": "Incense",
     "intro": "عودهای هندی؛ اسطوخودوس، مشک کشمیری، صندل، قهوه و رایحه‌های گل."},
    {"slug": "spices", "fa": "ادویه", "en": "Spices",
     "intro": "ادویه‌های آماده؛ خورشتی، بحرینی، مچبوس، سالاد سزار و سیب‌زمینی."},
]
CATEGORY = {c["slug"]: c for c in CATEGORIES}

# supplier list -> section, for the three lists that are already one thing
LIST_CATEGORY = {"candle": "candles", "beauty": "beauty", "ceramic": "ceramics"}

# "Other" is split by keyword, first match wins. Checked after normalisation.
OTHER_RULES = [
    ("نقره", "silver"),
    ("عود", "incense"),
    ("بافتنی", "knitted-flowers"),
    ("دسته گل", "knitted-flowers"),
    ("لیلیوم", "knitted-flowers"),
    ("آفتابگردان", "knitted-flowers"),
    ("ادویه", "spices"),
    ("پودر سیر", "spices"),
    ("عطر", "beauty"),
    ("استیکر", "small-gifts"),
    ("کارت پستال", "small-gifts"),
    ("پین", "small-gifts"),
]

# Spreadsheet text that means "not for sale any more".
SOLD_WORDS = ("فروخته شد", "فروش رفته", "موجود نیست")
# Silver is priced on the day — the owner wrote this instead of a number.
DAY_PRICE = re.compile(r"^قیمت\s*به\s*روز$")

# Spelling fixes, applied in order to every name. Each one is a correction of
# what the owner typed, not a rewrite, and import_lists.py prints every name it
# changes so the owner can see them (they are also in docs/REVIEW-FA.md).
# Colloquial spellings become the written form a shop uses (گلدون -> گلدان).
FIXES = [
    (r"ي", "ی"), (r"ك", "ک"),                        # Arabic keyboard letters
    (r"\s+", " "),
    (r"^ALLUREHOMMESPORT$", "عطر الورا Allure Homme Sport"),
    (r"\bدسبند\b", "دستبند"),
    (r"\bادوبه\b", "ادویه"),
    (r"\bاویز\b", "آویز"),
    (r"\bابی\b", "آبی"),
    (r"\bاباژور\b", "آباژور"),
    (r"\bافتابگردون\b", "آفتابگردان"),
    (r"\bگلدون\b", "گلدان"),
    (r"\bناخون\b", "ناخن"),
    (r"\bللیوم\b", "لیلیوم"),
    (r"\bسمبل\b", "سنبل"),                            # the painted flower is grape hyacinth
    (r"\bهایلاتر\b", "هایلایتر"),
    (r"\bتراور ماگ\b", "تراول ماگ"),
    (r"\bکارت پوستال\b", "کارت پستال"),
    (r"\bکوچ رنگی\b", "کوچک رنگی"),
    (r"\bکوچیک\b", "کوچک"),
    (r"\bفالی\b", "سفالی"),
    (r"\bاستیکردلفین\b", "استیکر دلفین"),
    (r"\bرژلب\b", "رژ لب"),
    (r"\bوکوچک\b", "و کوچک"),
    (r"\bتوت ?فرنگی\b", "توت‌فرنگی"),
    (r"\bتخم مرغ", "تخم‌مرغ"),
    (r"\bسوسیس تخم‌مرغ\b", "سوسیس و تخم‌مرغ"),
    (r"\bجا شمعی\b", "جاشمعی"),
    (r"\bجا قاشق و چنگالی\b", "جاقاشقی و چنگالی"),
    (r"\bجا کره ای\b", "جاکره‌ای"),
    (r"\bجا تخم‌مرغی\b", "جاتخم‌مرغی"),
    (r"\bزیر ماگی\b", "زیرماگی"),
    (r"\bزیر لیوانی\b", "زیرلیوانی"),
    (r"\bلیپ گلاس\b", "لیپ‌گلاس"),
    (r"\bپاپیه ماشه\b", "پاپیه‌ماشه"),
    (r"\bدسته دار\b", "دسته‌دار"),
    (r"\bلعاب دار\b", "لعاب‌دار"),
    (r"\bبلند کننده\b", "بلندکننده"),
    (r"\bحجم دهنده\b", "حجم‌دهنده"),
    (r"\bنیکس ژل\b", "نیکس‌ژل"),
    (r"\bطرح دار\b", "طرح‌دار"),
    (r" ای\b", "‌ای"),                                # استوانه ای -> استوانه‌ای (ZWNJ)
    (r" های\b", "‌های"),                              # شمع های -> شمع‌های
    (r"\+", " + "),
    (r"\s+", " "),
]


def clean_name(raw):
    """Return (name, [human-readable corrections])."""
    if raw is None:
        return None, []
    s = raw.strip()
    before = s
    for pat, rep in FIXES:
        s = re.sub(pat, rep, s)
    # digits inside Persian text are Persian (سایز 3 -> سایز ۳); Latin names keep theirs
    s = re.sub(r"(?<![A-Za-z])\d+(?![A-Za-z])", lambda m: fa_digits(m.group(0)), s).strip()
    notes = [f"«{before}» → «{s}»"] if s != before else []
    return (s or None), notes


def classify(collection, name):
    if collection in LIST_CATEGORY:
        return LIST_CATEGORY[collection]
    for word, slug in OTHER_RULES:
        if name and word in name:
            return slug
    return None


FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def fa_digits(x):
    return str(x).translate(FA_DIGITS)


def toman(n):
    """350000 -> '۳۵۰٬۰۰۰' (U+066C, the Persian thousands separator)."""
    return fa_digits(f"{n:,}".replace(",", "٬"))
