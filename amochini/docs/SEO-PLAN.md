# amochini.ir — 90-day SEO plan

## Read this first: the situation is better than a migration plan implies

Research into what Google currently holds for this domain found **exactly one
indexed URL — the homepage** — and the WordPress install is about six weeks
old (every product image sits in `wp-content/uploads/2026/08/`). Eleven
separate search queries, including `site:amochini.ir` and Persian
product-intent queries, returned only that homepage.

That reframes everything:

- **There is almost no ranking equity to protect.** The cutover is low-risk.
  Do not spend weeks building a 130-row redirect map for URLs Google has never
  seen.
- **The 130 product pages have never been indexed at all.** They did not exist
  as URLs — the draft rendered all of them into one page from a JavaScript
  array. Every one of them is net-new opportunity.
- **The health metric for the next 90 days is indexed-page count, not
  traffic.** It should go from 1 toward 150+. A "traffic drop" metric is
  meaningless from a base of one page.

Google is ~99.5% of search in Iran, so this is Google SEO. Domestic engines
are not worth any effort.

### Honest gap in this plan

Four of nine research angles did not complete — the account hit its monthly
spend limit mid-run. The missing ones were **Persian keyword research**,
**Iranian hosting/analytics specifics**, and **information-architecture
validation** (plus a completeness critic). So this plan is solid on technical
execution, migration and structured data, and **thinner than I would like on
specific keyword targets and on the Digikala/Torob marketplace play**. Those
are flagged where they appear. Re-run that research before committing budget
to content.

---

## Month 1 — get indexed, and get the basics honest

The entire month is about going from 1 indexed page to most of 153, and
filling in the things I could not invent.

### Week 1 — pre-cutover (do not skip any of this)

| # | Action | Why |
|---|---|---|
| 1 | Fill in `build/site_config.py` | Address and trust badges are the only launch blockers left. See [PLACEHOLDERS.md](PLACEHOLDERS.md). |
| 2 | **Confirm: are the prices Rial or Toman?** | A 10× error published in structured data is a public commitment. I read them as Rial and the build asserts it; one word from you settles it. |
| 3 | Export the WordPress URL list **and** `wp-content/uploads/` | Once WP is gone these cannot be recovered. [MIGRATION.md §1](MIGRATION.md) |
| 4 | Move Search Console to **DNS TXT verification** | If verification is a WordPress plugin's meta tag, it dies with WordPress — at exactly the moment you need GSC most. |
| 5 | Export 16 months of GSC Performance + Pages | Same reason. Do it in the same VPN session as #4. |
| 6 | Get a TLS certificate issued | `.ir` is genuinely hard: Sectigo (cPanel's default AutoSSL provider) refuses `.ir`; Let's Encrypt issues. Switch the provider or run acme.sh. |
| 7 | Confirm the web server is Apache or LiteSpeed | **nginx ignores `.htaccess` silently.** If it's nginx, every redirect is a no-op and you won't be told. |

### Week 2 — cutover

Follow [MIGRATION.md](MIGRATION.md) steps 3–5 in order. On launch day:

1. Submit `sitemap.xml` in Search Console.
2. **Request Indexing manually on ~12 URLs only**: the homepage, the three
   category pages, the brand pages for MVM / JAC / Lifan / Chery, and your
   four best-selling SKUs. The quota is roughly 10–12 URLs/day; all 130
   products would take two weeks of clicking and the sitemap will get them
   anyway.
3. Do **not** build a sitemap ping into anything — Google retired that
   endpoint at the end of 2023. `lastmod` in the sitemap is the scheduling
   signal that replaced it.
4. Flip `SCHEME = "https"` and uncomment the HTTPS block **only after**
   `curl -I https://amochini.ir/` returns 200 from outside Iran.

### Weeks 3–4 — the two things that actually gate growth

**Photograph the products.** This is the single biggest content gap and the
most valuable thing anyone can do for this site. Right now 130 products share
four stock images: the 77 discs share three (plain / drilled / slotted), all
50 pads share one, and the 3 drums borrow a disc photo. Near-identical images
across 130 pages weakens Google Images, and it is the main thin-content risk
these pages carry. Phone photos of real stock, one per model family, would be
a large improvement. Give them descriptive filenames
(`disk-charkh-mvm-x33-front.webp`), not random strings.

**Price the 14 unpriced SKUs.** `AMO-042, 046, 057, 092, 093, 104, 105, 108,
109, 110, 112, 113, 114, 118` currently render "استعلام قیمت" and carry no
`Offer` in their structured data — a fabricated price would be a
structured-data violation, so they cannot earn a product snippet until real
prices exist.

### Also in month 1 — the off-site work that probably outranks the site

Research found **no Google Business Profile, no Instagram and no Telegram
presence** for this business. For an Iranian local parts retailer these
plausibly drive more enquiries in the first three months than the website's
own organic search does.

- **Google Business Profile** — claim and fully verify it. Real address,
  real phone (09122650076), hours, category "Auto parts store", photos of the
  actual shop. This is what puts you in the local pack and on Maps.
- **Instagram and Telegram** — these are where Iranian parts buying actually
  happens. Once the handles exist, put them in `SOCIAL` in
  `build/site_config.py` and they appear in the footer and in the store's
  `sameAs` structured data. Until then the code omits them rather than
  linking to nothing.

### Month 1 exit criteria

- [ ] HTTPS live, `SCHEME = "https"`, canonical URLs all https
- [ ] `python3 build/validate.py` reports zero launch blockers
- [ ] Search Console on DNS verification, sitemap submitted
- [ ] Indexed page count climbing past ~50
- [ ] Rich Results Test passes on a product, a category and the home page
- [ ] Google Business Profile verified

---

## Month 2 — content that answers real questions

With the pages indexed, the job becomes earning queries the product pages
alone cannot.

### Build the keyword set properly first

**This is the part the incomplete research leaves open.** Before writing, do
the work I could not finish:

1. Google Keyword Planner and Google Trends, geo-targeted to Iran, for the
   three category terms and the brand × part combinations.
2. Cross-check against a Persian-specific tool (Mizfa Tools, Keywordchi) —
   international tools have patchy Persian volume data.
3. Capture **three layers** of each term: Persian script (both formal and
   colloquial), Finglish/transliterated (`lent tormoz`, `disk charkh`), and
   the English loanword.
4. Check the actual query patterns. The likely dominant template is
   `<part> <brand> <model> <axle>` — «لنت ترمز جلو ام‌وی‌ام ۳۱۵» — which is
   exactly what the product page titles already use. Confirm it rather than
   assume it.

### Write the articles that support the products

The site has a `/blog/` route reserved but no posts. Priority topics, chosen
because they map onto questions the product FAQs already answer and onto real
diagnostic intent:

1. علائم خرابی لنت ترمز — چه زمانی باید لنت را عوض کرد؟
2. فرق دیسک ساده، سوراخ‌دار (TRA-X) و شیاردار (XTRA) چیست؟
3. لرزش فرمان هنگام ترمز — علت و راه‌حل
4. لنت ترمز اورجینال یا طرح؟ چطور تشخیص بدهیم
5. کاسه چرخ یا دیسک — تفاوت سیستم ترمز کاسه‌ای و دیسکی
6. راهنمای انتخاب قطعات ترمز خودروهای چینی بر اساس مدل
7. هر چند کیلومتر باید لنت و دیسک را تعویض کرد؟
8. آب‌بندی لنت نو — چرا مهم است و چطور انجام می‌شود
9. چرا ترمز خودرو صدا می‌دهد؟ شش علت رایج
10. تراش دیسک چرخ بهتر است یا تعویض؟

Each one should link to the relevant category and to two or three specific
products. Write them as genuine answers — these are the queries where a
specialist shop can beat a marketplace, because Digikala does not explain
anything.

**Note on FAQ markup:** the site emits `FAQPage` JSON-LD, but Google retired
FAQ rich results in May 2026 (and HowTo in 2023). It is kept because it is
honest, valid markup that Bing and AI answer engines still read — treat it as
an AI-visibility play, not a Google rich-result play. Don't expect stars.

### Marketplace listings — flagged, not specified

The research consensus is that Iranian product search largely resolves inside
**Digikala** and **Torob** rather than on the open web, which would make
listing the 130 SKUs there the highest-ROI action available. **I could not
verify the mechanics** — whether Torob crawls product schema from your site
automatically or requires a merchant feed, and what format. That angle is one
of the four that failed. Establish it before investing, but treat it as the
top candidate for month 2 effort.

Note that **Google Merchant Center is not available to retailers in Iran**, so
Shopping surfaces are out regardless. The site's structured data is therefore
built for product *snippets* only, which is why it omits the
merchant-listing-only properties (`shippingDetails`, `hasMerchantReturnPolicy`,
`gtin`) — that is deliberate, not an oversight.

---

## Month 3 — consolidate, then decide where to push

### Measure what actually happened

By now there is real data. In Search Console:

- **Performance → Queries** — which Persian queries are landing, and on which
  pages. This is the first real evidence of what this catalogue can rank for.
- **Performance → Pages** — which of the 153 pages earn impressions. Expect a
  long tail of product pages with a handful of impressions each; that is the
  shape you want.
- **Indexing → Pages** — anything excluded, and why.

### The decisions to make from that data

1. **Brand × category pages.** Queries like «لنت ترمز ام‌وی‌ام» are likely
   real demand that currently has no dedicated page — brand pages cover all
   parts for a car, category pages cover all cars for a part, and nothing sits
   at the intersection. There are 45 possible combinations. Only build the
   ones the query data justifies, and only where there are enough products
   that the page isn't thin — I'd use "at least 3 products" as the floor.
   **Check Google's faceted-navigation and thin-content guidance before
   building any of them**; this was in the architecture research that didn't
   complete.
2. **More models, or more depth?** If brand pages are pulling impressions,
   widening the catalogue wins. If the blog posts are pulling, depth wins.
3. **Re-request indexing** on anything still unindexed after 90 days, and work
   out why — usually thin content or no internal links pointing at it.

### Keep doing

- Update prices, and rebuild. Prices are the thing Iranians search on
  («قیمت لنت ترمز …») and a stale price is worse than no price.
- Run `python3 build/validate.py` before every upload. It catches 10× price
  drift, broken links, duplicate titles, orphan pages, missing structured
  data, bidi-corrupted model codes, and the placeholders.
- Run `PORT=8901 python3 build/measure_weight.py` after any design change; it
  fails if a page crosses 150 KB.
- Ask for Persian-language Google reviews on the Business Profile. Once real
  reviews exist you can mark them up — **but only what is visibly on the
  page.** Never invent an `aggregateRating`: a rating with no reviews behind
  it is a manual-action risk that would strip rich results from the whole
  domain.

---

## Things not to do

- **Don't force HTTPS before the certificate exists.** It takes the site
  offline for users and Googlebot with no error message.
- **Don't remove the WordPress redirects** in `.htaccess` before September
  2027. Google expects a 301 to persist for at least a year.
- **Don't add an `aggregateRating`, a fake `gtin`, or an `mpn`** copied from
  your own SKU. All three are fabricated identifiers.
- **Don't set `priceValidUntil`.** A date in the past actively suppresses the
  listing, so a generator stamping "+30 days" silently kills every rich result
  the first month nobody rebuilds. It is omitted on purpose.
- **Don't add third-party scripts casually.** The site currently makes zero
  third-party requests, which is the single biggest reason it is fast from
  inside Iran — a blocked request there doesn't fail fast, it hangs, and the
  page waits. If you add analytics, load it `async` and test on a real Iranian
  connection.
- **Don't repeat the "100,000 parts" claim** from the old homepage on pages
  that show 130 SKUs, unless it's true of the physical shop and you say so.
- **Don't block `/wp-content/` in robots.txt.** The old product images live
  there; blocking it would deindex them from Google Images before the new
  pages have earned any image rankings of their own.
