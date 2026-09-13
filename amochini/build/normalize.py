# -*- coding: utf-8 -*-
"""
Normalize the raw amochini product catalogue into a canonical data file.

Fixes applied (each one is a real defect found in the source data):
  1. Arabic/Persian character folding      ي->ی  ك->ک  ة->ه  ى->ی  strip tatweel/harakat
  2. ZWNJ consistency  — source spells the same brand two ways:
     name field "ام وی ام" (plain space) vs brand field "ام‌وی‌ام" (U+200C)
  3. Brand mis-assignment — "سایر" (other) hides two real brands with real search
     demand: فاو (FAW) and گریت وال (Great Wall)
  4. Brand name drift  — names say "برلیان", brand field says "برلیانس"
  5. Word-order drift  — "دیسک چرخ ام وی ام 530 عقب" vs "دیسک چرخ عقب آریزو 6"
  6. Model + variant extraction (TRA-X / XTRA are product lines, not part of the model)
  7. ASCII slug generation for every product, brand and category
"""
import json, re, unicodedata

ZWNJ = "‌"

# ---------- 1. character folding -------------------------------------------
FOLD = {
    "ي": "ی",  # ARABIC YEH        ي -> ی
    "ى": "ی",  # ALEF MAKSURA      ى -> ی
    "ك": "ک",  # ARABIC KAF        ك -> ک
    "ة": "ه",  # TEH MARBUTA       ة -> ه
    "ۀ": "ه" + ZWNJ + "ا",  # HEH WITH YEH ABOVE ۀ
    "ـ": "",        # TATWEEL / kashida  ـ
}
HARAKAT = re.compile(r"[ً-ٰٟۖ-ۭ]")
AR_DIGITS = {chr(0x0660 + i): str(i) for i in range(10)}   # ٠-٩ -> 0-9
FA_DIGITS = {chr(0x06F0 + i): str(i) for i in range(10)}   # ۰-۹ -> 0-9
TO_FA = {str(i): chr(0x06F0 + i) for i in range(10)}


def fold(s):
    """Fold Arabic variants to Persian, strip diacritics, normalise digits to Latin."""
    if not s:
        return s
    s = unicodedata.normalize("NFC", s)
    for a, b in FOLD.items():
        s = s.replace(a, b)
    s = HARAKAT.sub("", s)
    for a, b in {**AR_DIGITS, **FA_DIGITS}.items():
        s = s.replace(a, b)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def to_fa_digits(s):
    """Latin digits -> Persian digits, for display text only. Never for schema."""
    return "".join(TO_FA.get(c, c) for c in str(s))


def search_key(s):
    """
    Aggressive key for the client-side search index.
    ZWNJ becomes a SPACE, not nothing: deleting it turns چت‌بات into چتبات which
    still fails to match چت بات; converting to space makes both resolve to the
    same two tokens.
    """
    s = fold(s).replace(ZWNJ, " ")
    s = re.sub(r"[^\w؀-ۿ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


# ---------- 2. canonical brands --------------------------------------------
# slug: ASCII, matches how Iranian shops actually spell these in URLs
# fa:   correct ZWNJ spelling for display
# alt:  every spelling seen in the wild -> feeds the search index and the 301 map
BRANDS = {
    "mvm":         dict(fa="ام" + ZWNJ + "وی" + ZWNJ + "ام", en="MVM",
                        alt=["ام وی ام", "امویام", "MVM", "ام-وی-ام", "چری کیو کیو"]),
    "jac":         dict(fa="جک", en="JAC", alt=["JAC", "جک موتور"]),
    "lifan":       dict(fa="لیفان", en="Lifan", alt=["Lifan"]),
    "chery":       dict(fa="چری", en="Chery", alt=["Chery", "چری", "آریزو", "تیگو"]),
    "haima":       dict(fa="هایما", en="Haima", alt=["Haima"]),
    "brilliance":  dict(fa="برلیانس", en="Brilliance", alt=["برلیان", "Brilliance", "برليانس"]),
    "changan":     dict(fa="چانگان", en="Changan", alt=["Changan", "چانگان"]),
    "geely":       dict(fa="جیلی", en="Geely", alt=["Geely", "جیلی"]),
    "bestune":     dict(fa="بست", en="Bestune", alt=["فاو بست", "Bestune", "بستون"]),
    "kmc":         dict(fa="کی" + ZWNJ + "ام" + ZWNJ + "سی", en="KMC",
                        alt=["KMC", "کی ام سی", "کرمان موتور"]),
    "capra":       dict(fa="کاپرا", en="Capra", alt=["Capra", "کاپرا"]),
    "cross":       dict(fa="کراس", en="Cross", alt=["CROSS", "کراس"]),
    "respect":     dict(fa="ریسپکت", en="Respect", alt=["Respect"]),
    "fidelity":    dict(fa="فیدیلیتی", en="Fidelity", alt=["Fidelity", "فیدلیتی"]),
    # --- split out of "سایر" (other): both have real search volume ---
    "faw":         dict(fa="فاو", en="FAW", alt=["FAW", "فاو"]),
    "great-wall":  dict(fa="گریت وال", en="Great Wall", alt=["Great Wall", "گریتوال", "هاوال", "وولکس"]),
}
FA_TO_SLUG = {}
for slug, b in BRANDS.items():
    FA_TO_SLUG[fold(b["fa"]).replace(ZWNJ, " ")] = slug
    for a in b["alt"]:
        FA_TO_SLUG[fold(a).replace(ZWNJ, " ")] = slug

# ---------- 3. canonical categories ----------------------------------------
CATEGORIES = {
    "brake-pads":  dict(fa="لنت ترمز", en="Brake Pads",
                        h1="لنت ترمز خودروهای چینی",
                        blurb="لنت ترمز جلو و عقب برای خودروهای چینی"),
    "brake-discs": dict(fa="دیسک چرخ", en="Brake Discs",
                        h1="دیسک چرخ خودروهای چینی",
                        blurb="دیسک چرخ (دیسک ترمز) جلو و عقب برای خودروهای چینی"),
    "brake-drums": dict(fa="کاسه چرخ", en="Brake Drums",
                        h1="کاسه چرخ خودروهای چینی",
                        blurb="کاسه چرخ عقب برای خودروهای چینی"),
}
FA_TO_CAT = {fold(v["fa"]): k for k, v in CATEGORIES.items()}

AXLES = {"جلو": dict(slug="front", en="Front", fa="جلو"),
         "عقب": dict(slug="rear",  en="Rear",  fa="عقب")}

# ---------- 4. product line variants ---------------------------------------
# TRA-X = cross-drilled, XTRA = drilled + slotted, base = plain vented/solid
VARIANTS = {
    "tra-x": dict(code="TRA-X", fa="سوراخ‌دار", en="Cross-drilled", img="disc-drilled"),
    "xtra":  dict(code="XTRA",  fa="سوراخ‌دار و شیاردار", en="Drilled & slotted", img="disc-slotted"),
    "base":  dict(code="",      fa="استاندارد", en="Standard", img="disc-plain"),
}

# ---------- 5. model transliteration ---------------------------------------
# Persian model tokens -> ASCII, for slugs only.
MODEL_TRANSLIT = {
    "آریزو": "arrizo", "تیگو": "tiggo", "شاسی": "shasi",
    "ایدو": "eado", "هاوال": "haval", "وولکس": "voleex", "پرایم": "prime",
    "کفشکی": "kafshaki", "اتومات": "automatic", "دنده ای": "manual",
    "دنده‌ای": "manual", "مدل": "", "و": "va",
    "جلو": "front", "عقب": "rear",
}


def slugify(s):
    """Persian/mixed text -> ASCII slug. Deterministic, no external deps."""
    s = fold(s).replace(ZWNJ, " ")
    s = re.sub(r"(?<![\w؀-ۿ])تی\s+(\d)", r"t\1", s)   # "تی 5" -> t5
    for fa, en in MODEL_TRANSLIT.items():
        s = re.sub(rf"(?<![\w؀-ۿ]){re.escape(fa)}(?![\w؀-ۿ])", f" {en} ", s)
    for fa, slug in sorted(FA_TO_SLUG.items(), key=lambda kv: -len(kv[0])):
        s = re.sub(rf"(?<![\w؀-ۿ]){re.escape(fa)}(?![\w؀-ۿ])",
                   f" {BRANDS[slug]['en'].lower().replace(' ', '-')} ", s)
    s = re.sub(r"[؀-ۿ]+", " ", s)          # drop anything still Persian
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)
