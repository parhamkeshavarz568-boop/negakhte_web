# -*- coding: utf-8 -*-
"""Turn the raw scraped PRODUCTS array into the canonical catalogue."""
import json, re, sys, collections
sys.path.insert(0, __import__("os").path.dirname(__file__))
from normalize import (ZWNJ, fold, slugify, search_key, to_fa_digits,
                       BRANDS, CATEGORIES, AXLES, VARIANTS, FA_TO_SLUG, FA_TO_CAT)

# The catalogue as extracted from the original single-page draft. This is the
# INPUT you edit to change prices or add products; products.json is generated.
RAW = __import__("os").path.join(__import__("os").path.dirname(__file__),
                                 "data", "products.source.json")

# Brand tokens that appear inside product NAMES (superset of the brand field,
# because the source misfiles FAW and Great Wall under "سایر").
# (token, brand) — token seen in a product NAME implies this brand.
# `strip=False` means the token is a MODEL name, not the brand itself, so it must
# stay in the extracted model (وولکس Voleex and هاوال Haval are Great Wall models).
NAME_BRAND_HINTS = [
    ("فاو بست", "bestune", True), ("گریت وال", "great-wall", True),
    ("هاوال", "great-wall", False), ("وولکس", "great-wall", False),
    ("فاو", "faw", True), ("برلیان", "brilliance", True),
    ("ام وی ام", "mvm", True), ("آریزو", "chery", False), ("چری", "chery", True),
    ("تیگو", "chery", False), ("جیلی", "geely", True), ("چانگان", "changan", True),
    ("هایما", "haima", True), ("لیفان", "lifan", True), ("ریسپکت", "respect", True),
    ("فیدیلیتی", "fidelity", True), ("کاپرا", "capra", True),
    ("KMC", "kmc", True), ("CROSS", "cross", True), ("جک", "jac", True),
    ("بست", "bestune", True),
]

# ---------------------------------------------------------------------------
# Bidi visual-entry corrections.
#
# Both of these are the same class of bug: someone typed a Latin/numeric model
# code into a right-to-left text field, and what they saw on screen (correct)
# is not what got stored (reversed).
#
# 1. Brilliance model ranges. The catalogue stores the SAME cars in BOTH
#    directions — "230-220" three times and "220-230" twice — which is
#    internally inconsistent whatever the intent, and would produce two
#    different URLs for the same car family. Under UAX#9 a digit run after a
#    Persian letter is retyped EN->AN and the hyphen becomes a number
#    separator, so "220-230" renders as "230-220" and vice versa. Normalised
#    to ascending order with a slash: U+002F is not a bidi number separator,
#    so it cannot flip, and it reads correctly in both directions.
#
# 2. Changan "35 CS". The model is CS35 — that is how Changan, the Iranian
#    importer and every buyer writes it. "35 CS" is the on-screen reversal of
#    CS35 captured verbatim. Left uncorrected, a search for the string the
#    entire market uses returns nothing, and "changan-35-cs-front" becomes a
#    permanent URL built on a typo.
MODEL_FIXES = [
    (r"\b230-220\b", "220/230"), (r"\b220-230\b", "220/230"),
    (r"\b330-320\b", "320/330"), (r"\b320-330\b", "320/330"),
    (r"(?<![A-Za-z])35\s+CS(?![A-Za-z])", "CS35"),
]


def fix_bidi_entry(name):
    for pat, rep in MODEL_FIXES:
        name = re.sub(pat, rep, name)
    return name


# Words to strip when isolating the MODEL from a product name.
NOISE = ["دیسک چرخ", "لنت ترمز", "کاسه چرخ", "جلو", "عقب", "مدل",
         "TRA-X", "XTRA", "و"]


def detect_brand(name, raw_brand):
    """Prefer a brand named in the product title over the (sometimes wrong) field."""
    n = fold(name).replace(ZWNJ, " ")
    for token, slug, _strip in NAME_BRAND_HINTS:
        if re.search(rf"(?<![\w؀-ۿ]){re.escape(fold(token))}(?![\w؀-ۿ])", n, re.I):
            return slug, (token, "name")
    rb = fold(raw_brand).replace(ZWNJ, " ")
    if rb in FA_TO_SLUG:
        return FA_TO_SLUG[rb], (raw_brand, "field")
    return None, (raw_brand, "unmatched")


def detect_variant(name):
    n = fold(name).upper()
    if "TRA-X" in n:
        return "tra-x"
    if "XTRA" in n:
        return "xtra"
    return "base"


def extract_model(name, brand_slug):
    """Everything left after removing category, brand, axle and variant words."""
    m = fold(name).replace(ZWNJ, " ")
    keep = {fold(t) for t, s_, strip in NAME_BRAND_HINTS if not strip}
    for token, slug, strip in NAME_BRAND_HINTS:
        if slug == brand_slug and strip:
            m = re.sub(rf"(?<![\w؀-ۿ]){re.escape(fold(token))}(?![\w؀-ۿ])", " ", m, flags=re.I)
    if brand_slug in BRANDS:
        for a in [BRANDS[brand_slug]["fa"]] + BRANDS[brand_slug]["alt"]:
            fa = fold(a).replace(ZWNJ, " ")
            if fa in keep:
                continue
            m = re.sub(rf"(?<![\w؀-ۿ]){re.escape(fa)}(?![\w؀-ۿ])", " ", m, flags=re.I)
    for w in NOISE:
        m = re.sub(rf"(?<![\w؀-ۿ]){re.escape(w)}(?![\w؀-ۿ])", " ", m, flags=re.I)
    return re.sub(r"\s+", " ", m).strip(" -")


def main():
    raw = json.load(open(RAW, encoding="utf-8"))
    out, issues = [], []
    for r in raw:
        name_src = fix_bidi_entry(fold(r["n"]))
        if name_src != fold(r["n"]):
            issues.append(f"{r['s']}: bidi visual-entry fix "
                          f"{fold(r['n'])!r} -> {name_src!r}")
        brand, why = detect_brand(name_src, r["b"])
        if brand is None:
            issues.append(f"{r['s']}: brand unresolved ({why})")
            brand = "other"
        cat = FA_TO_CAT.get(fold(r["c"]))
        if cat is None:
            issues.append(f"{r['s']}: category unresolved ({r['c']})")
            continue
        axle = AXLES.get(fold(r["a"]))
        if axle is None:
            issues.append(f"{r['s']}: axle unresolved ({r['a']})")
            continue
        variant = detect_variant(name_src)
        model = extract_model(name_src, brand)
        if r["b"] != "سایر" and brand != FA_TO_SLUG.get(fold(r["b"]).replace(ZWNJ, " ")):
            issues.append(f"{r['s']}: brand field '{r['b']}' -> reassigned '{brand}'")
        if r["b"] == "سایر" and brand != "other":
            issues.append(f"{r['s']}: rescued from 'سایر' -> '{brand}'")

        bfa = BRANDS[brand]["fa"] if brand in BRANDS else "سایر"
        cfa = CATEGORIES[cat]["fa"]
        # canonical display name, one consistent word order everywhere:
        #   <category> <brand> <model> <axle> [<variant>]
        parts = [cfa, bfa, model, axle["fa"]]
        if variant != "base":
            parts.append(VARIANTS[variant]["code"])
        title = re.sub(r"\s+", " ", " ".join(p for p in parts if p)).strip()

        mslug = slugify(model)
        slug = "-".join(x for x in [brand, mslug, axle["slug"],
                                    variant if variant != "base" else ""] if x)

        price = r["p"] if isinstance(r["p"], int) else None
        out.append(dict(
            sku=r["s"], slug=slug, title=title, name_source=r["n"],
            category=cat, brand=brand, model=model, axle=axle["slug"],
            variant=variant,
            price_irr=price,                       # Rial, integer, no separators
            price_toman=(price // 10) if price else None,
            in_stock=bool(r["k"]) and price is not None,
            # Drums borrow the plain-disc studio shot rather than the dark
            # "mood" disc photo: mixing a dramatic dark image in with
            # white-studio ones made the grid look like a mismatched
            # catalogue. All three are placeholders until real photos exist.
            image=VARIANTS[variant]["img"] if cat == "brake-discs" else (
                "cat-brake-pads" if cat == "brake-pads" else "disc-plain"),
            search=" ".join(sorted(set(
                search_key(f"{title} {r['n']} {BRANDS.get(brand,{}).get('en','')} "
                           f"{' '.join(BRANDS.get(brand,{}).get('alt',[]))} "
                           f"{CATEGORIES[cat]['en']} {r['s']}").split()))),
        ))

    # URLs are /<category>/<slug>/ so slugs need only be unique WITHIN a category.
    seen = collections.Counter((p["category"], p["slug"]) for p in out)
    for (cat, sl), n in seen.items():
        if n > 1:
            clash = [p for p in out if p["category"] == cat and p["slug"] == sl]
            issues.append(f"SLUG COLLISION in {cat} '{sl}': {[p['sku'] for p in clash]}")
            for i, p in enumerate(clash[1:], 2):
                p["slug"] = f"{sl}-{i}"
    for p in out:
        p["url"] = f"/{p['category']}/{p['slug']}/"

    json.dump(out, open("build/data/products.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"wrote {len(out)} products -> build/data/products.json")
    print(f"\n--- {len(issues)} data issues corrected ---")
    for i in issues:
        print("  " + i)
    print("\n--- brand distribution after correction ---")
    for b, n in collections.Counter(p["brand"] for p in out).most_common():
        print(f"  {b:14s} {n:3d}   {BRANDS.get(b,{}).get('fa','?')}")
    print("\n--- sample ---")
    for p in out[:3] + [p for p in out if p["brand"] == "great-wall"][:2]:
        print("  " + json.dumps({k: p[k] for k in ("sku","slug","title","brand","model","variant","price_toman","in_stock")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
