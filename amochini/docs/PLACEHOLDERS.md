# What you must fill in before launch

Everything below is a **placeholder carried over from the original draft**. I did
not invent real values for any of it — a fabricated address or phone number on a
live shop is worse than an obvious blank.

Almost all of it lives in **one file**: `build/site_config.py`. Edit that, run
`python3 build/build.py`, and all 153 pages update at once.

---

## 1. BLOCKING — the site should not go live without these

| What | Where | Why it blocks |
|---|---|---|
| **Shop phone number** | `CONTACT["phone_display"]` and `["phone_tel"]` | It is the *only* way to order. There is no checkout. The draft's `۰۲۱–۱۲۳۴۵۶۷۸` is fake. Appears on all 153 pages, in `tel:` links, and in the store's structured data. |
| **Mobile / WhatsApp number** | `CONTACT["mobile_*"]`, `CONTACT["whatsapp"]` | Every product page has a "سفارش در واتساپ" button pointing at it. |
| **Street address** | `CONTACT["street"]`, `["city"]`, `["region"]`, `["postal_code"]` | Currently «نشانی نمونه، خیابان نمونه، پلاک ۰۰». Goes into `AutoPartsStore` structured data and drives local-pack eligibility. A fake address can get a Google Business Profile suspended. |
| **Email** | `CONTACT["email"]` | Set to `info@amochini.ir` — **confirm this mailbox actually exists** before publishing it. |
| **Currency check** | `COMMERCE["display_divisor"]` | See §4 below. Getting this wrong shows every price off by 10×. |

`phone_tel` and `mobile_tel` must be **E.164**: `+98` then the number without the
leading zero. `۰۲۱ ۸۸۱۲۳۴۵۶` → `+982188123456`.

---

## 2. STRONGLY RECOMMENDED

| What | Where | Why |
|---|---|---|
| **e-Namad (نماد اعتماد الکترونیکی)** | `TRUST["enamad_code"]` | Iranian online shops are expected to display it; many buyers will not order without it. Paste the whole `<a>…</a>` snippet e-Namad gives you. A labelled empty slot renders in the footer until you do, so the layout is already correct. |
| **Samandehi (ساماندهی)** | `TRUST["samandehi_code"]` | Same. |
| **Instagram / Telegram handles** | `SOCIAL` | The draft linked Facebook, Twitter and Google+. Google+ shut down in 2019; Facebook and Twitter are filtered in Iran — all three were dead links and I removed them. Any handle left empty is simply not rendered, so no broken icons. |
| **Shop coordinates** | `CONTACT["latitude"]`, `["longitude"]` | Left as `None` on purpose: the code omits `geo` from structured data rather than publishing a wrong pin. Fill in from Google Maps / Neshan and they appear. |
| **Real product photos** | `public/assets/img/` | See §3. |

---

## 3. Product photography — the biggest content gap

The source data has **two** images for **130** products:

- all 77 brake discs share three generic disc photos (plain / drilled / slotted)
- all 50 brake pads share **one** photo
- the 3 brake drums currently borrow the disc photo

The third home-page category card was labelled **چراغ** (headlight) with a
headlight photo, but its filter pointed at **کاسه چرخ** (brake drums) and there
is no headlight category in the data at all. I fixed the label and the link; the
photo is still a headlight and should be replaced with a brake-drum photo.

This matters for SEO: near-identical images across 130 pages weakens Google
Images and adds to the thin-content risk those pages already carry. Even phone
photos of real stock, one per model family, would be a large improvement.

Drop new files in `public/assets/img/` and update the `image` field logic in
`build/build_catalog.py`.

---

## 4. Confirm the currency — Rial or Toman?

The source prices run 14,586,000 → 60,885,000 with no unit recorded. I read them
as **Rial**, because:

- the draft's cart said «۰ **ریال**»
- as Rial they are 1,458,600 → 6,088,500 **Toman**, which is a plausible 2026
  price band for brake parts
- as Toman they would be 14.5M → 60.8M Toman per brake pad, which is not

So the site **stores Rial, displays Toman** (`display_divisor = 10`), and the
structured data emits the Rial value with `priceCurrency: "IRR"` — Toman has no
ISO 4217 code, so this is the only correct way to express it.

**If those numbers are actually Toman**, set `display_divisor = 1` in
`build/site_config.py` and tell me — the schema needs the reciprocal change too.

---

## 5. Business-policy values I guessed

Sensible defaults, all in `build/site_config.py`. They appear in visible text, so
correct them if wrong:

- `free_shipping_over_toman = 10,000,000` — the draft said «بالای ۱۰۰ میلیون»
  without a unit; I read that as 100M Rial = 10M Toman
- `return_days = 7` — from the draft's «۷ روز ضمانت بازگشت وجه»
- Opening hours — from the draft's «شنبه تا پنج‌شنبه، ۸ الی ۱۷»
- The "قطعات اصلی / تضمین اصالت" claim in the footer and on brand pages — **only
  keep this if it is true.** A false authenticity claim is a legal and
  reputational risk, and it appears on every page.

---

## 6. Product names worth a second look

Corrections I made to the catalogue, and one I could not resolve:

- **4 products were filed under «سایر» (other)** but name real brands. Moved to
  their own brand pages: `AMO-080` and `AMO-112/113` → گریت وال (Great Wall),
  `AMO-108` → فاو (FAW).
- **«برلیان» → «برلیانس»** — the names said Brilian, the brand field said
  Brilliance. Standardised on برلیانس.
- **«ام وی ام» → «ام‌وی‌ام»** — names used a plain space, the brand field used a
  ZWNJ half-space. Standardised on the ZWNJ form (what Digikala and Torob use).
- **`AMO-037/038/039` «چری تی ۵»** — I kept this as written and slugged it
  `chery-t5`. If it means the **Chery Tiggo 5** it should read «چری تیگو ۵», which
  is also what people search for. **Please confirm.**

## 7. The 14 products with no price

`AMO-042, 046, 057, 092, 093, 104, 105, 108, 109, 110, 112, 113, 114, 118`

They render as «استعلام قیمت» (ask for a price), are marked out of stock, and
carry **no `Offer`** in their structured data — a fabricated price would be a
structured-data violation. They are still in the sitemap at lower priority so
they can rank for their model name. Add prices in
`build/data/products.source.json` → rebuild, and they become normal products.
