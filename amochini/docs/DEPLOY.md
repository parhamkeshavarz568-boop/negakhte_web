# Deploying amochini.ir

## What to upload

Upload **the contents of `public/`** — not the folder itself — into your host's
web root (on cPanel that is `public_html/`).

```
public/
├── index.html                 home
├── brake-pads/                50 products
├── brake-discs/               77 products
├── brake-drums/               3 products
├── brands/                    index + 16 brand pages
├── about/  contact/
├── 404.html
├── .htaccess                  ← easy to miss: it is a dotfile
├── robots.txt  sitemap.xml  search-index.json  site.webmanifest
├── favicon.svg  favicon.ico  apple-touch-icon.png  icon-*.png
└── assets/  css/ js/ fonts/ img/
```

**Do not upload `build/` or `docs/`.** They are the source, not the site. (The
`.htaccess` blocks `.py`, `.json`, `.md` and friends anyway, as a backstop —
except `search-index.json` and `site.webmanifest`, which the site needs.)

### Two things people forget

1. **`.htaccess` is hidden.** Turn on "show hidden files" in cPanel File Manager
   or your FTP client, or it silently doesn't get uploaded — and then none of the
   redirects, caching, compression or security headers exist.
2. **Upload as binary.** Some old FTP clients "helpfully" convert line endings in
   `.woff2` and `.jpg`, corrupting them. Use SFTP, or cPanel's own uploader, or
   upload a `.zip` and extract it server-side.

The fastest reliable route on cPanel: zip `public/`, upload the zip, *Extract*,
then move the files up one level into `public_html/`.

---

## Before you upload

- [ ] Filled in `build/site_config.py` — see [PLACEHOLDERS.md](PLACEHOLDERS.md)
- [ ] Ran `python3 build/build.py` after editing it
- [ ] Ran `python3 build/validate.py` and it says `✓ no errors`
- [ ] Exported the old WordPress URLs — see [MIGRATION.md](MIGRATION.md) §1
- [ ] Generated the redirect map and rebuilt
- [ ] **SSL certificate is active** on amochini.ir

That last one matters: `.htaccess` force-redirects everything to HTTPS. Without a
certificate the site is unreachable. Check cPanel → *SSL/TLS Status* → run
*AutoSSL*. Let's Encrypt works from Iranian hosts; most cPanel installs offer it
in one click. If it is not ready yet, comment out block 1 of `.htaccess` and
uncomment it once the certificate is installed.

---

## Rebuilding after a change

Everything is generated. Never edit files in `public/` — the next build
overwrites them.

| To change | Edit | Then |
|---|---|---|
| Phone, address, socials, policies | `build/site_config.py` | `python3 build/build.py` |
| Prices, stock, add/remove products | `build/data/products.source.json` | `python3 build/build_catalog.py && python3 build/build.py` |
| Page text, headings, FAQs | `build/pages.py` | `python3 build/build.py` |
| Styling | `build/assets/site.css` | `python3 build/build.py` |
| Search / filters behaviour | `build/assets/site.js` | `python3 build/build.py` |
| Redirects, caching, headers | `build/templates/htaccess.tpl` | `python3 build/build.py` |

Then re-run `python3 build/validate.py` and re-upload `public/`.

Requires Python 3.8+. No pip packages, no Node, no build toolchain — deliberately,
so this still builds in five years.

### Updating prices

Prices are the thing that changes most. In `build/data/products.source.json`,
`"p"` is the price **in Rial** (`null` = "ask us"). Change the numbers, then:

```bash
python3 build/build_catalog.py && python3 build/build.py && python3 build/validate.py
```

Re-upload the changed HTML plus `search-index.json` and `sitemap.xml`.

---

## After you upload

```bash
# 1. homepage loads over https
curl -sI https://amochini.ir/ | head -3

# 2. security headers and compression are live
curl -sI -H 'Accept-Encoding: gzip' https://amochini.ir/ \
  | grep -iE 'content-encoding|x-content-type|content-security'

# 3. a product page
curl -sI https://amochini.ir/brake-pads/mvm-315-front/ | head -1

# 4. 404 works and is not a soft 200
curl -sI https://amochini.ir/definitely-not-a-page/ | head -1

# 5. sitemap and robots
curl -s https://amochini.ir/robots.txt
curl -s https://amochini.ir/sitemap.xml | head -5
```

Then in a browser, on a phone:

- Persian renders right-to-left with no reversed punctuation
- the font loads (text is Vazirmatn, not Tahoma fallback)
- the hamburger menu opens
- typing «لنت» in the header search shows suggestions
- the hero vehicle finder lands on a filtered category page
- a product page's «تماس و سفارش» dials, and «سفارش در واتساپ» opens WhatsApp

### Validate the structured data

- Rich Results Test — <https://search.google.com/test/rich-results>
- Schema Markup Validator — <https://validator.schema.org/>

Test a product page, a category page and the home page. Expect `Product`,
`BreadcrumbList`, `FAQPage`, `ItemList` and `AutoPartsStore` to be found with no
errors.

### Then follow [MIGRATION.md](MIGRATION.md) §4–6

Verification, Search Console, and keeping WordPress recoverable for 30 days.

---

## Performance expectations

The site ships with **zero third-party requests**. No CDN font, no analytics, no
tag manager. That is deliberate: from inside Iran a blocked third-party request
does not fail fast, it *hangs*, and the page waits for it.

Measured, gzipped, as the server sends it:

| | cold first visit | repeat visit |
|---|---|---|
| HTML (home) | 5.8 KB | 5.8 KB |
| CSS | 5.0 KB | cached |
| JS (deferred) | 3.0 KB | cached |
| Font — subset variable WOFF2, weights 100–900 | 68.3 KB | cached |
| Hero image — WebP, 640w on mobile | 27.9 KB | cached |
| **Above-the-fold total** | **110 KB** | **5.8 KB** |

Plus 60 KB of lazy-loaded category thumbnails below the fold. Product pages are
lighter still — 5.8 KB of HTML and no hero.

For comparison, the original single-page draft was **474 KB of HTML** (324 KB
gzipped) on *every* page view, because the images were base64-inlined and
therefore uncacheable. The font is now the largest single asset, and it is
cached for a year.

If you later add analytics, put it in `ANALYTICS` in `build/site_config.py` and
load it `async`. Test the site afterwards on a real Iranian connection — a
blocked analytics script is the single most common cause of a slow Iranian site.
