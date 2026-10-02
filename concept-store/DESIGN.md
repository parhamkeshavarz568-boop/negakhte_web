# DESIGN.md — the concept store

The single source of truth for every visual decision. If a value you need is
not here, add it here first, then use it. `build/assets/site.css` implements
this file; `validate.py` checks the contrast pairs on every build.

---

## 1. Subject, audience, the one job

**Subject.** A small Iranian concept store: Ayshid's handmade candles, glazed
ceramics, crochet flowers, silver, Nixgel / Niura / ELORA beauty, incense,
spices, 3D stickers and postcards. Many pieces are one-offs; twenty have
already sold.

**Audience.** Someone on their phone, usually arriving from Instagram or from
a link a friend sent, looking for a gift or for something for their own shelf.

**The one job.** *Let someone fall for a piece, then send its code.* There is
no cart. Every piece has a code (`S-10`) and every product page ends in the
shop's DM.

**The design consequence.** Unlike amochini, this shop has *excellent*
photography: 203 photos, every one shot in the same corner, the same
travertine ledge, the same late sun through the same six-paned window. The
photos are the site. Everything else is quiet so they can be loud.

---

## 2. Colour: the room the photos were taken in

Measured, not picked. Across all 178 catalogue photos the set runs from
`#f2d6b0` (lit stone) through `#c9a680` (mid) to `#83674c` (deep shadow). The
page ground is deliberately **paler and less saturated than the brightest lit
stone**, so every photo reads as a sunlit window into the room rather than a
sticker on the page.

| Token | Hex | Role |
|---|---|---|
| `--ground` | `#f5eee4` | **Dominant.** Limestone. The page. |
| `--ground-2` | `#ebe1d3` | Photo wells (seen before an image loads), the order band. |
| `--ink` | `#2a2119` | All primary text. 13.7:1 on ground. |
| `--ink-2` | `#6b5a4a` | Secondary text, prices' units, meta. 5.7:1 on ground, 5.1:1 on ground-2. |
| `--rule` | `#ddd0bf` | Hairlines. Carries no text. |
| `--clay` | `#a3472a` | **The one accent**, taken from the glazes and the orange candles. 5.2:1 either way round with ground. |
| `--clay-deep` | `#86391f` | Hover state of `--clay`. |
| `--sun` | `#f0cf9f` | The window light (§5). Never a text or fill colour. |

**Clay is rationed:** the primary button, the step numerals, the focus ring,
the "copy code" link, the window in the logo mark. Not headings, not borders,
not decoration.

There is no dark mode, on purpose. The photos are sunlit and warm, and a dark
page around them reads as a museum at night, which is the wrong room.
`color-scheme: light` is declared so browsers do not invert form controls.

---

## 3. Type: two faces, six sizes

| Face | Use | Why |
|---|---|---|
| **Markazi Text** (Borna Izadpanah, OFL), 400–700 | the shop's name, headings, product names, the intro lines | A text face drawn from Persian book typography. It has the inked, slightly hand-set quality of a label written for a single object, which makes this read as a shop rather than a catalogue. The same designer drew Lalezar, which the repo already ships. |
| **Vazirmatn** (Saber Rastikerdar, OFL), 100–900 | prices, codes, buttons, all small text | Even, clear numerals at 13–15px; the same pinned v33.003 that amochini vendors. |

Both are self-hosted subsets (46 KB + 56 KB). No Google Fonts, because it is
SNI-filtered in Iran and a stalled font request blocks first paint.

| Token | Size | Use |
|---|---|---|
| `--t-1` | 13px | meta, codes, sold labels, footer |
| `--t-2` | 15px | body, UI, prices |
| `--t-3` | 22px | product names on cards (Markazi runs small) |
| `--t-4` | 32px | section heads |
| `--t-5` | 40–60px | page titles |
| `--t-6` | 56–136px | the shop's name, home only |

Persian digits everywhere (`۴۶۸٬۰۰۰`, with U+066C as the thousands
separator). The exception is **product codes, which stay Latin** (`S-10`) and
are always isolated LTR: they are what people type into a DM, and Latin is
what every keyboard types the same way.

---

## 4. Space, radius, shadow

- Spacing: `--s-1`…`--s-6` = 8 / 16 / 24 / 40 / 64 / 104px. Gutter 16 / 32 / 48px.
- **One radius: 2px.** Square enough to read as printed cards and paper labels.
  Chips are the one pill (999px), because a row of filters must not read as a row of buttons.
- **No box shadows.** The only shadow on the site is the window's (§5), and
  the real ones inside the photographs.
- Every photo on a grid is **4:5**. The masters come in four ratios, so
  `make_images.py` crops to where the object is (colour departing from the
  beige set), not to the centre, which would cut off the taper candles
  and the jewellery busts. Product pages show the **uncropped** photo.

---

## 5. The signature: the window light

Every photograph shares one light source, a six-paned window in low sun. The
page is that room, so **that window's light falls on the page too**: across
the shop's name and the hero photos alike, which is what makes the photos
sit *in* the page rather than on it.

- Drawn as an inline SVG: 2×3 panes, skewed −32° to the angle the shadows lean
  in the photos, blurred, filled `--sun`, `mix-blend-mode: multiply`.
- Feathered with a radial mask, so it **never has an edge**. If you can see
  where it stops, it is wrong.
- Placements: the home hero (strongest, 0.74), section and about headers (0.6),
  the order band (0.55). Never on a product photo, which already has its own.
- **The one motion:** as you scroll, the light slides down and across
  (`animation-timeline: scroll()`), the way it moves over the stone in an
  afternoon. Static where unsupported; off under `prefers-reduced-motion`.

Everything else is still: hover on photos is a 3.5% scale over 0.9s, and
navigation cross-fades via view transitions.

---

## 6. Components

- **Card**: 4:5 photo, name (Markazi `--t-3`), price (`۳۵۰٬۰۰۰ تومان`), or
  «قیمت روز» for silver, «قیمت را بپرسید» for unpriced pieces.
- **Sold**: never deleted. They gather at the foot of each section under
  «به خانهٔ تازه رفتند» ("went to a new home"), smaller, desaturated, unlinked.
  They show the range of what the shop makes, and invite "make me one like that".
- **Order block**: the code, large; «کپی کد و نام» copies a ready-to-paste DM
  ("سلام! این قطعه را می‌خواهم: S-10 — ماگ لعابی جنگلی"); one button per configured
  channel, the first in clay; on phones a "send to a friend" share sheet.
- **Buy bar** (phones, product pages): the price and «سفارش با کد S-10»,
  always in reach.
- **Hero shelf**: one large print, one leaning behind it, one laid over its
  corner with a ground-coloured border, as if set down on a table.
