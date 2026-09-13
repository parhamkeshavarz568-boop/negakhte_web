# WordPress → static: don't lose your rankings

You are replacing a live WordPress site with static HTML on the **same domain**.
That is the good case — no domain change, no Change of Address in Search Console.
But every URL Google currently has indexed still has to resolve to something.

**The one thing that cannot be undone: once WordPress is off, its URL list is
gone.** Export it first. Everything below hangs off that.

---

## Step 1 — Export the old URLs (do this while WordPress is still up)

Any one of these works. The first is easiest.

### Option A — the sitemap (30 seconds)
Yoast and Rank Math both publish one. Open whichever of these loads:

```
https://amochini.ir/sitemap_index.xml
https://amochini.ir/sitemap.xml
https://amochini.ir/wp-sitemap.xml
```

Follow the child sitemaps (`product-sitemap.xml`, `page-sitemap.xml`, …) and
copy every `<loc>` into a plain text file, one per line.

Quick way, from any machine with `curl`:

```bash
curl -s https://amochini.ir/sitemap_index.xml \
  | grep -oE 'https?://[^<]+\.xml' \
  | xargs -I{} curl -s {} \
  | grep -oE '<loc>[^<]+' | sed 's|<loc>||' \
  | sort -u > old-urls.txt
```

### Option B — Search Console (best, shows what Google actually knows)
Search Console → **Pages** → *Indexed* → **Export**. Also grab
**Performance → Pages**, sorted by clicks: those are the URLs that actually earn
traffic and matter most.

### Option C — from WordPress itself
WP Admin → Tools → Export → *All content* → download the XML, then:

```bash
grep -oE '<link>[^<]+' export.xml | sed 's|<link>||' | sort -u > old-urls.txt
```

Save the result as `old-urls.txt`. **Keep a copy somewhere safe** — you cannot
regenerate it later.

> I could not fetch these myself: this build environment's network policy blocks
> `amochini.ir`, so I have no view of the live site. The redirect map is
> therefore generated from *your* export, not guessed.

---

## Step 2 — Generate the redirect map

```bash
python3 build/make_redirects.py old-urls.txt
python3 build/build.py
```

`make_redirects.py` matches each old URL against all 130 products using the
*normalised* Persian text, so it copes with percent-encoded slugs, Arabic-vs-
Persian character drift (ي/ی, ك/ک), ZWNJ inconsistency and Persian digits.

It prints three groups:

- **matched** — written to `build/data/redirects.generated.conf`, each rule
  annotated with the product and a confidence score
- **skipped** — already covered by the structural rules in `.htaccess`
  (`/product-category/…`, `/wp-json/`, feeds, …)
- **UNMATCHED** — printed with its top three candidates

**Map the unmatched ones by hand.** The script deliberately refuses to guess when
two products score closely — pointing `lent-tormoz-jac-s5-jelo` at the wrong JAC
model is worse than sending it to the category page. Put your hand-written rules
in `build/data/redirects.manual.conf` using the same format:

```apache
  RewriteRule ^product/lent-tormoz-jac-s5-jelo/?$ /brake-pads/jac-5s-front/ [R=301,L]
```

`build.py` concatenates both files into `.htaccess`. Re-run it after editing.

Prioritise by traffic: a URL with clicks in Search Console deserves a hand-made
redirect; one with none can fall through to the category page.

---

## Step 3 — Cutover, in this order

1. **Back up WordPress** — full files + database. Non-negotiable.
2. Confirm `old-urls.txt` is saved somewhere off the server.
3. Upload `public/` to the host **into a staging folder**, e.g.
   `public_html/new/`. Do not overwrite WordPress yet.
4. Check the staging copy renders: Persian text, RTL layout, fonts loading,
   images, the search box, the vehicle finder.
5. **Confirm SSL is active on `amochini.ir`.** The `.htaccess` force-redirects to
   HTTPS. If no certificate is installed, every request will fail. cPanel →
   *SSL/TLS Status* → *Run AutoSSL*. If HTTPS is not ready, comment out block 1
   of `.htaccess` until it is.
   (Your product images are currently served over plain `http://` — so this may
   genuinely not be set up yet. Check before cutover, not after.)
6. Move WordPress aside — rename `public_html` contents into `public_html/old-wp/`
   rather than deleting. You may need to read from it.
7. Move the static files into `public_html/`.
8. Upload `.htaccess` **last**.

## Step 4 — Verify immediately after cutover

```bash
# homepage: 200, and https
curl -sI https://amochini.ir/ | head -3

# a redirect you generated: expect 301 and the right Location
curl -sI "https://amochini.ir/product/<an-old-slug>/" | grep -iE 'HTTP|location'

# dead WordPress surface: expect 410
curl -sI https://amochini.ir/wp-json/ | head -1

# http and www both land on the canonical host in ONE hop
curl -sI http://www.amochini.ir/ | grep -iE 'HTTP|location'
```

Then walk the top 10 URLs from your Search Console clicks export and confirm each
one lands somewhere sensible.

## Step 5 — Tell Google

1. Search Console → **Sitemaps** → submit `https://amochini.ir/sitemap.xml`
2. **URL Inspection** on the homepage → *Request indexing*. Do the same for the
   three category pages. (Manual requests are rate-limited; spend them on the
   pages that matter.)
3. Watch **Pages** for a week. A rise in *Not found (404)* means a redirect is
   missing — the report lists the URLs, so feed them back through
   `make_redirects.py`.
4. Expect ranking wobble for **2–6 weeks**. That is normal even for a clean
   migration. Don't panic-change things in week one; you'll lose the ability to
   tell what caused what.

> Search Console is generally unreachable from Iranian IPs without a VPN. That
> is an access nuisance, not a risk to the property.

## Step 6 — Keep WordPress recoverable for 30 days

Keep `old-wp/` and the database dump for at least a month. If traffic drops hard
and you cannot find why, being able to compare against the old site is worth far
more than the disk space.

---

## What the `.htaccess` already handles without any export

Even with no `old-urls.txt` at all, these never 404:

| Old URL | Becomes |
|---|---|
| `/product-category/…` | the matching category page, else `/brake-discs/` |
| `/product/…` (unmapped) | `/brake-discs/` |
| `/shop/` | `/brake-discs/` |
| `/cart/`, `/checkout/`, `/my-account/` | `/contact/` |
| `/?p=123`, `/?page_id=12` | `/` |
| `/?s=query` | `/brake-discs/` |
| `/wp-content/uploads/2026/08/TVuDo….jpg` | the real disc photo |
| other `/wp-content/uploads/…` | **410 Gone** |
| `/wp-json/`, `/xmlrpc.php`, `/feed/`, `/author/…` | **410 Gone** |
| `/wp-admin/…` | `/` |
| `/about`, `/contact` (+ Persian spellings) | `/about/`, `/contact/` |

**410 rather than 404 is deliberate** for the WordPress-only surface: 410 tells
Google the URL is permanently gone and it drops out of the index in days rather
than lingering for months as a soft 404.
