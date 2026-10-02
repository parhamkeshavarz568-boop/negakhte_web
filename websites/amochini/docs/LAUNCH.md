# Launch checklist — amochini.ir

Everything in `public/` is the site. Upload its **contents** to the web root
(so `public/index.html` becomes `/index.html`), including the dotfile
`.htaccess`. Nothing is compiled at the server: it is static HTML, CSS, one
small JS file, two fonts and a folder of images.

Run through this in order. The first three are blocking.

---

## 1. BLOCKING — the two trust badges

`TRUST["enamad_code"]` and `TRUST["samandehi_code"]` in
`build/site_config.py` are empty, and `validate.py` reports them on every
build. An Iranian commercial site without **اینماد** is a site most buyers
will not phone, and without **ساماندهی** it is legally exposed.

Get the codes, paste them in, rebuild. Nothing else in the build has to change.

## 2. BLOCKING — decide about the fabricated price history

`build/data/price-history.json` currently holds an **invented** twelve-week
rising series for all 116 priced products, written by `build/seed_prices.py`
at your instruction. What is true and what is not:

- **True:** every product's *current* price, the one a customer reads and
  pays. The last point of every series is the real catalogue figure, and
  `validate.py` asserts it against the schema.org Offer on all 116 pages.
- **Invented:** the path behind it — the chart, the percentage change, the
  index, the biggest-mover tiles.

Three mitigations are in place so this cannot become a search-spam problem:

1. **Nothing invented reaches structured data.** schema.org carries the
   current Offer only. The Dataset block describes the published feed files,
   which exist, and carries a `disambiguatingDescription` saying the history
   is illustrative.
2. **The published feeds flag it.** `prices.json` carries
   `synthetic_history: true` and a note, so the flag travels with the data.
3. **The page says it.** One sentence in the price board's footnote:
   «قیمت امروز هر کالا واقعی است؛ نمودار و درصد تغییر تا تکمیل ثبت روزانه،
   نمونه‌ای است.»

**To make it all real**, which is the better site:

```bash
rm build/data/price-history.json build/data/SYNTHETIC
python3 build/snapshot_prices.py --date 2026-07-01   # a price you know
python3 build/snapshot_prices.py --date 2026-08-01
python3 build/snapshot_prices.py                     # today
```

Real and seeded observations share one format, so you can also keep the seed
and let `snapshot_prices.py` append truth on top of it. Delete
`build/data/SYNTHETIC` and the footnote disappears by itself.

## 3. BLOCKING — get the certificate, then flip one line

The site publishes `http://` canonicals because that is what currently
resolves. That costs a ranking signal, and Chrome marks the address bar
**"Not secure"** on a site that asks people to phone the number it publishes.

Let's Encrypt **does** issue for `.ir`. Their Subscriber Agreement v1.7 (June
2026) added sanctions wording that looked like a blanket exclusion, but v1.8
(6 July 2026) replaced it, and they continue to serve permitted
non-governmental users where exemptions apply. The obstacle is practical: the
ACME endpoint is reachable only intermittently from inside Iran, so use
**DNS-01** (no inbound connection needed) or have the host obtain it. Sectigo,
cPanel's default AutoSSL provider, will **not** issue for `.ir` — do not
waste a day on AutoSSL.

Once `curl -I https://amochini.ir/` returns 200 with a valid chain **from
outside Iran**:

```bash
# build/site_config.py
SCHEME = "https"
```

then uncomment the HTTPS block at the bottom of
`build/templates/htaccess.tpl`, rebuild, and re-upload. That one constant
rewrites every canonical, `og:url`, JSON-LD `@id` and sitemap URL.

---

## 4. Upload

```
public/  ->  the web root
```

Confirm afterwards:

| check | expected |
|---|---|
| `curl -I http://amochini.ir/` | `200` |
| `curl -I http://amochini.ir/brake-pads/` | `200` (directory URLs work) |
| `curl -I http://amochini.ir/nothing-here/` | **`404`**, and our 404 page |
| `curl -I http://amochini.ir/?p=123` | `301` to a real page |
| `curl -sI http://amochini.ir/assets/css/site.css \| grep -i encoding` | `gzip` or `br` |

**If the host runs nginx, not Apache/LiteSpeed, `.htaccess` is silently
ignored** and every WordPress redirect, the 404 page and the compression
rules stop working. Ask the host which it is before you upload; if it is
nginx, tell me and I will write the nginx equivalent.

## 5. Search Console — the same day

1. Add the property at <https://search.google.com/search-console> as a
   **Domain property** (DNS TXT record) — it covers http, https and every
   subdomain at once, so it survives the HTTPS flip in step 3.
2. **Sitemaps → submit** `sitemap.xml`. It lists 154 URLs, each with a real
   `lastmod` (a product's is its latest price date, not the build date —
   Google discounts sitemaps where everything changed "today").
3. **URL Inspection → Request indexing** for these five only. Do not bulk
   request; it does nothing and the quota is small:
   `/`, `/prices/`, `/brake-pads/`, `/brake-discs/`, `/brands/`
4. Expect first indexing in **3–7 days** for a fresh domain. Do not panic on
   day two and do not buy links.

Also submit to **Bing Webmaster Tools** — it imports directly from Search
Console, so it is two clicks, and Bing has real share in Iran.

## 6. IndexNow — after every deploy

Bing, Yandex, Seznam, Naver and Yep crawl within minutes off an IndexNow
ping. **Google ignores IndexNow** and has said so repeatedly — this is not a
Google tactic.

The key is already published at `/e8d8143105718dd4e8f37def76cb6820.txt`. After each upload:

```bash
curl "https://api.indexnow.org/indexnow?url=http://amochini.ir/&key=e8d8143105718dd4e8f37def76cb6820"
```

## 7. The daily price snapshot — this is the whole product

```bash
python3 build/snapshot_prices.py    # records only what actually changed
python3 build/build.py
```

Then re-upload `public/`. Do it every morning you change a price. Every run
makes the index, the charts and the deltas more real and the seeded data less
of the picture — and a price site that is genuinely updated daily is the one
durable SEO advantage this business has over a catalogue that sits still.

---

## What is already done, so nobody redoes it

| | |
|---|---|
| canonical, og, twitter on all 155 pages | ✓ unique titles and descriptions, verified by `validate.py` |
| `lang="fa-IR" dir="rtl"` | ✓ every page |
| hreflang | ✗ **deliberately absent.** Google wants it only where multiple language or region versions of a page exist. This is one Persian site; adding self-referencing hreflang buys nothing and three quarters of implementations in the wild carry errors. |
| structured data | ✓ Organization, WebSite, Product+Offer (real prices, IRR), BreadcrumbList, ItemList, CollectionPage, FAQPage, Dataset |
| fabricated identifiers | ✗ no `mpn`, no `gtin`, no `aggregateRating` — `validate.py` fails the build if any appear |
| sitemap | ✓ 154 URLs, real per-URL `lastmod`, no `priority`/`changefreq` (Google ignores both) |
| robots.txt | ✓ allows everything that should be crawled, blocks filter/sort states and dead WordPress surface, points at the sitemap |
| 301 map from the old WordPress URLs | ✓ in `.htaccess`, fenced with a do-not-remove-before date |
| social card | ✓ one branded 1200×630 `og-card.jpg`, correct aspect for WhatsApp, Telegram and Twitter |
| Core Web Vitals | ✓ CLS **0.000** across 24 page/viewport combinations, LCP 40–300 ms locally, no long tasks. The 2026 thresholds are LCP < 2.5 s, INP < 200 ms, CLS < 0.1 |
| page weight | ✓ heaviest first load **144 KB** against a 150 KB budget |
| accessibility | ✓ 0 WCAG AA contrast failures and 0 targets under 24×24, computed in a real browser |
| thin / scaled content | ✓ measured: 475–623 words per product page, median **56%** of each page's 6-grams not shared with other product pages, **0** pages under 20% distinctive |
| images | ✓ AVIF/WebP/JPEG, sized to their real boxes, `width`/`height` on every one |
