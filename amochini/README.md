# عمو چینی — amochini.ir

## Run it on your laptop

The built site is committed, so a fresh clone is already a working website —
nothing to install, nothing to compile.

```powershell
# Windows PowerShell
git clone https://github.com/parhamkeshavarz568-boop/negakhte_web.git
cd negakhte_web\amochini\public
python -m http.server 8000
```

```bash
# macOS / Linux
git clone https://github.com/parhamkeshavarz568-boop/negakhte_web.git
cd negakhte_web/amochini/public
python3 -m http.server 8000
```

Then open <http://localhost:8000> — not `http://0.0.0.0:8000`, which some
Windows browsers refuse. Ctrl+C in the terminal stops the server.

Already have the repo? `git pull` first.

No Python on the machine? Any static server does: `npx serve -l 8000` with
Node, or `php -S localhost:8000`, or the "Live Server" extension in VS Code
(right-click `public/index.html` → Open with Live Server).

### Do not double-click index.html

Opening the file directly gives a broken page with no fonts and no styling.
Every asset path is root-absolute (`/assets/css/site.css`) and every page is a
directory (`/brake-discs/`), so both need a server at the root of `public/`.
That is how the site will actually be served — it is not a bug to fix.

### What a local server cannot show you

Three things are the web server's job, so `python -m http.server` skips them
and the pages are still correct:

| | why |
|---|---|
| the WordPress 301 redirects | they live in `.htaccess`, which only Apache/LiteSpeed reads |
| the real 404 page | you will get Python's plain "File not found"; open `/404.html` directly to see ours |
| link prerendering | Speculation Rules ship as an HTTP header, which needs the real server config |

### Seeing the price movement

The live site holds one price per product so far, so every row reads
«ثبت‌شده» with no percentage and no sparkline — correct, because a trend
through one point would be invented. To see what it looks like once history
accumulates:

```powershell
cd negakhte_web\amochini\build
python make_preview.py
```

That writes a throwaway build with synthetic movement to a temp folder (it
prints the path), carries `noindex` on every page, and never touches `public/`
or the real price history. Serve that folder the same way.

---

**Read `DESIGN.md` before changing anything visual.** It is the design system:
six colours, two typefaces, five type sizes, five spacing steps, one radius, no
shadows, one signature element and one moment of motion. If a change needs a
value that is not in that file, the value gets added there first.


Static site for an Iranian auto-parts retailer selling brake components
(لنت ترمز, دیسک چرخ, کاسه چرخ) for Chinese cars sold in Iran.

153 pages generated from a 130-product catalogue. No framework, no npm, no
build toolchain — Python 3.8+ and nothing else, so it still builds in five
years.

## Quick start

```bash
sh build/all.sh               # full rebuild: font, images, icons, 153 pages, checks
```

Or just the pages, when only copy or data changed:

```bash
python3 build/build.py        # generate public/  (~2 seconds)
python3 build/validate.py     # check it          (must say "build is valid")
```

Then upload the **contents of `public/`** to the web root. Full instructions:
[docs/DEPLOY.md](docs/DEPLOY.md).

## Before it goes live

Two documents matter more than this one:

- **[docs/PLACEHOLDERS.md](docs/PLACEHOLDERS.md)** — the business details still
  to fill in. The street address and the e-Namad / ساماندهی badges are the
  remaining launch blockers; `validate.py` lists them on every run.
- **[docs/MIGRATION.md](docs/MIGRATION.md)** — amochini.ir currently runs
  WordPress. **Export its URL list and `wp-content/uploads/` before taking it
  down.** Those cannot be recovered afterwards.

## Layout

```
build/                      source — edit here
  site_config.py            every business-specific value, in one file
  data/
    products.source.json    the catalogue you edit (prices, stock, new SKUs)
    products.json           generated — canonical, corrected, slugged
    images.json             generated — which renditions exist on disk
  normalize.py              Persian folding, ZWNJ, slugs, brand/category tables
  build_catalog.py          source catalogue -> canonical catalogue
  pages.py                  page bodies and JSON-LD
  layout.py                 shared head / header / footer
  build.py                  writes everything into public/
  validate.py               self-check: links, SEO, schema, prices, Persian
  check_font.py             proves the font subset renders every string
  make_font.py              rebuild the Vazirmatn subset
  make_images.py            rebuild the AVIF/WebP/JPEG renditions
  make_redirects.py         WordPress URL export -> 301 rules
  measure_weight.py         real page weight in headless Chromium
  check_layout.py           CLS/LCP, scroll-height stability, overflow, reveals
  templates/htaccess.tpl    Apache/LiteSpeed config
  assets/                   site.css, site.js
  original/                 the draft this was built from, and image sources

public/                     generated — NEVER edit, the next build overwrites it
docs/                       deployment, migration, placeholders, SEO plan
```

## URL map

```
/                                    home
/brake-pads/                         50 products
/brake-discs/                        77 products
/brake-drums/                        3 products
/brands/                             index
/brands/<brand>/                     16 brand pages
/<category>/<brand>-<model>-<axle>/  130 product pages
/about/  /contact/  /404.html
/robots.txt  /sitemap.xml  /search-index.json
```

## How to change things

| To change | Edit | Then |
|---|---|---|
| phone, address, socials, policies | `build/site_config.py` | `build.py` |
| prices, stock, add a product | `build/data/products.source.json` | `build_catalog.py` then `build.py` |
| page copy, headings, FAQs | `build/pages.py` | `build.py` |
| styling | `build/assets/site.css` | `build.py` |
| search / filter behaviour | `build/assets/site.js` | `build.py` |
| redirects, caching, headers | `build/templates/htaccess.tpl` | `build.py` |
| images | `build/original/images/` | `make_images.py` then `build.py` |

Always finish with `python3 build/validate.py`.

## Decisions worth knowing about

**Prices are stored in Rial and displayed in Toman.** The source values only
make sense as Rial, and the old cart said «ریال». Schema.org requires ISO 4217
and Toman has no code, so the JSON-LD emits the Rial integer with
`priceCurrency: "IRR"` while the page shows Toman. `validate.py` asserts all
116 offers match the catalogue exactly — a 10× drift here would publish wrong
prices into search results. If the numbers turn out to be Toman, change
`display_divisor` in `site_config.py` and say so.

**The site is `http://`, not `https://`, by default.** Not an oversight. The
one URL Google has indexed is `http://`, and `.ir` domains are hard to
certificate — Sectigo, cPanel's default AutoSSL provider, refuses `.ir`;
Let's Encrypt issues. Publishing https canonicals against a domain with no
certificate takes the site offline for users *and* Googlebot, silently. One
constant (`SCHEME`) flips every canonical, og:url, JSON-LD `@id` and sitemap
entry together, and the HTTPS redirect ships commented with the enable
sequence. See [docs/MIGRATION.md](docs/MIGRATION.md).

**Zero third-party requests.** No CDN font, no analytics, no tag manager. The
draft loaded its font from cdn.jsdelivr.net, which is Cloudflare anycast —
subject to SNI-based blocking in Iran, where a blocked request doesn't fail
fast, it hangs, and first paint waits for it. cdnjs and unpkg are the same
network, so they are not fallbacks. The font is vendored and subset instead.

**`brand` in the product structured data is not the car make.** The catalogue's
brand field is the vehicle a part fits, not who manufactured the part.
Emitting `"brand": "MVM"` on a brake disc asserts MVM made it — false, and the
kind of misleading markup that earns a domain-wide manual action. The vehicle
is expressed via `isAccessoryOrSparePartFor` instead; only TRA-X and XTRA,
which are genuine product lines, carry a `brand`.

**Catalogue corrections were applied, not assumed.** The source data had two
classes of bidi visual-entry corruption — Brilliance model ranges stored in
both directions (`230-220` and `220-230` for the same cars) and Changan
`35 CS` where the model is `CS35` — plus four products filed under «سایر» that
actually name Great Wall and FAW, and inconsistent برلیان/برلیانس spelling.
`build_catalog.py` prints every correction it makes; `validate.py` fails if
the corrupted patterns reappear.

**All 130 products are ASMCO**, and the business supplies ASMCO parts in Iran.
That matters for the markup: schema.org `brand` is the part manufacturer
(ASMCO), never the car the part fits, and TRA-X / XTRA are ASMCO product lines
so they are emitted as a product-series property rather than as brands.

**Product photography is still the biggest content gap.** 130 products share
four stock images. It is the top item in the SEO plan.

## Performance

Measured in headless Chromium at DPR 2, over the wire:

| | mobile | desktop |
|---|---|---|
| home | 120 KB | 140 KB |
| product | 90 KB | 116 KB |
| repeat visit | ~6–10 KB | ~6–10 KB |

**CLS 0.000** on all 21 page/viewport combinations; LCP 48–176ms off
localhost. Navigation is prerendered on link hover via Speculation Rules and
cross-fades via view transitions.

The draft was 474 KB of HTML (324 KB gzipped) on every view. Details and
method: [docs/MEASUREMENTS.md](docs/MEASUREMENTS.md).

## Licence

The site content belongs to عمو چینی. Both typefaces are SIL OFL 1.1 —
Vazirmatn (Saber Rastikerdar) and Lalezar (Borna Izadpanah). Their licences
ship at `public/assets/fonts/OFL-Vazirmatn.txt` and
`public/assets/fonts/OFL-Lalezar.txt` and must stay with the fonts.
