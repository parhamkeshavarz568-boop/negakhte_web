# Concept store (name to come)

Static site for a small Iranian concept store: Ayshid's handmade candles,
ceramics, crochet flowers, silver, Nixgel / Niura / ELORA beauty, incense,
spices, stickers and postcards. Persian, right-to-left, phone-first.

It belongs to the same house as `negakhte_main`, and is designed to *feel* it
without saying it: negakhte's exact palette (cream, ink, oxblood, gold, teal)
and its marks — the gold ◆ after the name, the gold highlighter under
headings, the hard gold offset shadow on buttons. See [DESIGN.md](DESIGN.md) §2–3.

**170 pages from 179 catalogue rows:** home, 8 sections, 159 product pages,
about and 404. No framework, no npm: Python 3.8+ with Pillow, numpy and
fontTools (plus `brotli` for the font step).

> **Upload-ready, in preview mode.** `dist/concept-store-upload.zip` can go on
> a host today, and every page says `noindex` until launch. The shop's name,
> contact channels and domain were not in the export; `validate.py` lists them
> as launch blockers on every run. Owner's checklist (Persian):
> [docs/REVIEW-FA.md](docs/REVIEW-FA.md). Upload guide (Persian):
> [docs/UPLOAD-FA.md](docs/UPLOAD-FA.md).

## Run it on your laptop

The built site is committed, so a fresh clone is already a working website:

```powershell
cd negakhte_web\concept-store\public
python -m http.server 8000
```

Open <http://localhost:8000>. Do not double-click `index.html`: every path is
root-absolute (`/assets/site.css`), so it needs a server at the root of
`public/`, which is also how it must be deployed.

## Where the content came from

The owner's export, four price lists (`.xlsx`) and four zips of photos, one
pair per collection, was on the Desktop in `consept store/`.
`build/ingest.py` brought it in:

```
build/original/lists/     the four spreadsheets, byte-for-byte (candle, beauty, other, ceramic)
build/original/photos/    203 JPEG masters (q90, 4:4:4, native size) from 206 PNGs;
                          3 byte-identical duplicates dropped
                          MANIFEST.json maps every master back to its zip, filename and sha256
```

The spreadsheets do **not** hold their photos in cells. Each photo floats
over the sheet, anchored to a row, so `import_lists.py` has to work out which
photo is which product. Three things in that file were measured, not assumed,
and the importer encodes them as rules:

1. **Stacks.** Ten SOFAL rows have 2–9 photos piled on one cell. The row's
   photo is the **top one**, the only one visible in Excel. In every stack it is
   also the only photo nudged to the sheet's standard 5.2pt offset, so two
   independent signals agree on all ten rows, and the visible photo matches
   the row's name every time. The 25 photos underneath are *unassigned*, not
   guessed at (`docs/unassigned-photos.jpg`).
2. **Offsets.** Two photos in "Other" are anchored to rows 5 and 10 with a
   100pt offset on 100pt-tall rows, so they really sit in rows 6 and 11.
   Anchors are resolved against the real row heights.
3. **Matching.** Thumbnails are matched to masters by pixel distance, and the
   run fails if a match is weak or a master is claimed twice.

It also corrects spelling (colloquial → written, ZWNJ, Arabic ي/ك, Persian
digits), printing every change and keeping the original as `name_as_typed`.
Four priced rows with no name were named from their photo and flagged.

## Build

```sh
sh build/all.sh            # everything: import → images → fonts → icons → pages → checks → zip
```

or step by step:

```sh
python build/import_lists.py --force   # spreadsheets → data/products.source.json (overwrites edits!)
python build/make_images.py            # masters → AVIF + WebP renditions (incremental)
python build/make_font.py              # Markazi Text + Vazirmatn subsets
python build/make_icons.py             # favicon.svg + apple-touch-icon.png
python build/build.py                  # data → public/   (~1 second)
python build/validate.py               # must end with "build is valid"
python build/make_upload.py            # validate, then public/ → dist/concept-store-upload.zip
```

## Deploy

1. `python build/make_upload.py` → `dist/concept-store-upload.zip` (51 MB,
   1,716 files). It refuses to package a build that fails validation.
2. Upload it into `public_html/` and **Extract there**. The zip holds the
   *contents* of `public/`, so `index.html` and `.htaccess` land at the root.
3. Check: home opens on the wine entrance; `/xyz/` shows «این قفسه خالی است»
   (the `.htaccess` 404 rule works); `/candles` redirects to `/candles/`.

Step by step in Persian, with cPanel / DirectAdmin / FileZilla:
[docs/UPLOAD-FA.md](docs/UPLOAD-FA.md).

**In a folder instead of the root** (say `example.ir/shop/`): set
`SITE["base"] = "/shop/"`, rebuild, and extract into `public_html/shop/`. Every
link, image, srcset, font and the 404 rule follow that one value; this was
tested by serving a `/shop/` build from a real `shop/` folder.

**Launch day:** fill in `SITE` (name, `url`) and `CONTACT` in
`build/site_config.py`, set `SITE["launch"] = True` (drops the `noindex`),
rebuild, `make_upload.py`, upload again. `validate.py`'s blocker list should be
empty.

`.htaccess` (from `build/templates/htaccess.tpl`) sets caching (a year for
images, fonts and the `?v=`-fingerprinted CSS/JS; HTML always revalidated),
gzip/brotli, the AVIF MIME type many hosts still lack, the trailing-slash
redirect, www → bare domain, and plain security headers. HTTPS is **not**
forced: forcing it on a host without a certificate takes the site down. The
template explains the safe order. nginx ignores `.htaccess`; the site still
works there, without those extras.

## How to change things

| To change | Edit | Then |
|---|---|---|
| name, phone, Instagram, domain, address, folder, launch | `build/site_config.py` | `build.py` |
| a price, mark sold, rename a piece | `build/data/products.source.json` | `build.py` |
| which pieces are on the home page / section covers | `build/site_config.py` (`HOME`, `COVERS`) | `build.py` |
| section names and intros, spelling rules | `build/catalog.py` | `build.py` |
| styling | `build/assets/site.css` (read `DESIGN.md` first) | `build.py` |
| add a new piece | photo into `build/original/photos/<list>/`, an entry in `products.source.json` with a **new** code | `make_images.py`, `build.py` |

`status` is one of `available` (has `price_toman`), `day` (silver, priced on
the day), `ask` (no price yet) or `sold`. **Codes never change once
published**, because customers quote them. A sold piece keeps its code and
moves to the foot of its section; it is never deleted.

## URL map

```
/                              home
/<section>/                    candles, ceramics, knitted-flowers, silver, beauty,
                               small-gifts, incense, spices
/<section>/<code>/             one per piece for sale, e.g. /ceramics/s-10/
/about/  /404.html  /robots.txt  (/sitemap.xml once the domain is set)
```

## Decisions worth knowing about

**Ordering is by message, not by cart.** Every piece has a code (`S-10`). The
product page copies a ready-made message ("سلام! این قطعه را می‌خواهم: S-10 —
ماگ لعابی جنگلی") and opens the shop's Instagram DM (`ig.me/m/…`), Telegram,
WhatsApp (prefilled) or phone. Only channels set in `site_config.py` appear.

**Prices are taken as Toman.** A 50,000 sticker and a 570,000 candle only make
sense in Toman. Structured data publishes the Rial value with `IRR`, because
Toman has no ISO code. Confirm with the owner (REVIEW-FA §2).

**Nothing is published that is not known.** No domain means no canonical, no
`og:url`, no sitemap and no JSON-LD, rather than pointing them at a guess.
Unconfigured order buttons render (so the design can be reviewed) but are
inert, and `validate.py` lists them as a launch blocker.

**Zero third-party requests.** Fonts are self-hosted subsets. The only outbound
links are the shop's own channels.

**Images.** Grid tiles are a subject-aware 4:5 crop at 360/540/720; product
pages carry the uncropped photo at 1080; link previews use a 480×600 JPEG,
since Telegram and WhatsApp are where these links get shared. AVIF first, WebP
fallback. Every `<img>` ships its true width and height.

## Weight

Measured from `public/`:

| | raw | gzip |
|---|---|---|
| home HTML | 21.7 KB | 3.8 KB |
| section HTML (candles) | 27.7 KB | 3.6 KB |
| product HTML | 11.7 KB | 2.7 KB |
| site.css / site.js | 21.8 / 2.2 KB | 5.9 / 1.0 KB |
| fonts (once, cached) | 46 + 56 KB | — |

A grid tile is 8–17 KB as AVIF at phone sizes. Images are lazy below the fold;
the hero photo is `fetchpriority="high"`.

The repo cost: `public/` is 52 MB (1,716 files, almost all images) and the
masters are 57 MB. It is committed, like amochini's, so the uploadable output
is reviewable next to its source.

## Licence

Content and photographs belong to the shop. Markazi Text (Borna Izadpanah) and
Vazirmatn (Saber Rastikerdar) are SIL OFL 1.1; their licences ship next to the
fonts in `public/assets/fonts/` and must stay with them.
