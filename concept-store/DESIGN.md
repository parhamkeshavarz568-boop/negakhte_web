# DESIGN.md — the concept store

The single source of truth for every visual decision. If a value you need is
not here, add it here first, then use it. `build/assets/site.css` implements
this file; `validate.py` checks every text/ground pair on every build.

---

## 1. Subject, audience, the one job

**Subject.** A small Iranian concept store: Ayshid's handmade candles, glazed
ceramics, crochet flowers, silver, Nixgel / Niura / ELORA beauty, incense,
spices, 3D stickers and postcards. Many pieces are one-offs.

**Audience.** Someone on their phone, usually arriving from Instagram or from a
link a friend sent, looking for a gift or something for their own shelf.

**The one job.** *Let someone fall for a piece, then send its code.* No cart:
every piece has a code (`S-10`) and every product page ends in the shop's DM.

**The two consequences.**
- The photography is excellent and uniform (203 photos, one corner, one
  window, one late sun), so **the photos are the site**; everything else is
  quiet so they can be loud.
- The shop belongs to the same house as **negakhte**. It must *feel* related —
  colour, marks, the way a button presses — without saying so anywhere.

---

## 2. Colour: negakhte's palette, used for a shop

The house colours are negakhte's own values, unchanged. The concept store adds
two of its own: a wine for the entrance, and the sun.

| Token | Hex | From | Role |
|---|---|---|---|
| `--ground` | `#F5EFE6` | negakhte | **Dominant.** Cream paper, with negakhte's grain. |
| `--ground-2` | `#ECE2D2` | negakhte | Photo wells (before an image loads). |
| `--paper` | `#FBF7EF` | negakhte | The white border of a print; chip fill. |
| `--ink` | `#1F1A15` | negakhte | Text. 15.1:1 on ground. |
| `--ink-2` | `#6C6255` | negakhte | Secondary text. 5.2:1 on ground, 4.7:1 on ground-2. |
| `--rule` | `#D9CDB8` | negakhte | Hairlines. Carries no text. |
| `--oxblood` | `#7A2E1F` | negakhte | **The brand colour.** Primary buttons, links, the active chip, the logo mark. 8.2:1. |
| `--oxblood-deep` | `#5A1F12` | negakhte | Hover. |
| `--gold` | `#C99846` | negakhte | **Marks, never text on cream:** the ◆, the offset shadow, the highlighter, the shelf strip, the light on dark. |
| `--gold-ink` | `#7E5D25` | negakhte | Gold that carries text on cream (eyebrows, "ask for price"). 5.3:1. |
| `--gold-light` | `#E6C487` | ours | Gold that carries text on wine (9.5:1) and teal (4.5:1). |
| `--teal` | `#2D5C5C` | negakhte | The ordering band, and nothing else. |
| `--wine` | `#3F1610` | ours | The entrance and the footer: oxblood taken down into shade — the room before the sun reaches it. |
| `--wine-2` | `#2A0E09` | ours | The wine's edges. |
| `--sun` | `#F0CF9F` | ours | The window light on cream. |

**The page in colour, top to bottom:** wine entrance → gold shelf strip → cream
shelves → teal ordering band → wine footer. The page opens and closes in the
house's brand colour.

No dark mode: the photos are sunlit and warm. `color-scheme: light` is declared.

---

## 3. The marks negakhte and the shop share

None of these says "negakhte". Together they say *same house*.

| Mark | negakhte | here |
|---|---|---|
| **◆** a small gold square at 45° | after the brand name | after the shop's name — wordmark, footer, the hero's huge name |
| **The highlighter** — a gold bar under the lower third of the words | under the oxblood word in the headline | under every section heading and page title (`.hl`) |
| **The offset shadow** — a hard 4px gold shadow, no blur | the primary button; it lifts on hover | every primary button, and the phone buy bar |
| **The card lift** — rise 4px, a flat gold edge appears beneath | test cards | collection tiles and product photos |
| **The ornament eyebrow** — a 2rem rule, then small text | above the headline | above every page title, in `--gold-ink` |
| **The grain** — a faint fractal noise over the ground | the whole page | the whole page (dark grain on cream, light grain on wine and teal) |

---

## 4. Type: two faces, six sizes

| Face | Use | Why |
|---|---|---|
| **Markazi Text** (Borna Izadpanah, OFL), 400–700 | the shop's name, headings, product names, print captions | A text face drawn from Persian book typography, with the inked, hand-set quality of a label written for one object. It is what keeps the shop its own thing while the colours say "family". |
| **Vazirmatn** (Saber Rastikerdar, OFL), 100–900 | prices, codes, buttons, small text | negakhte's typeface. Even numerals at 13–15px. |

Both self-hosted subsets (46 KB + 56 KB): Google Fonts is SNI-filtered in Iran.

| Token | Size | Use |
|---|---|---|
| `--t-1` | 13px | meta, codes, sold labels, footer |
| `--t-2` | 15px | body, UI, prices |
| `--t-3` | 22px | product names on cards |
| `--t-4` | 34px | section heads |
| `--t-5` | 40–60px | page titles |
| `--t-6` | 60–152px | the shop's name, home only |

Persian digits everywhere (`۴۶۸٬۰۰۰`). Product codes stay Latin and LTR (`S-10`):
they are what people type into a DM.

---

## 5. The entrance

The first screen has to stop a thumb mid-scroll, so the home page does not open
on cream.

- **The room in shade.** A full-screen wine field (radial: a warmer `#6A2717`
  glow behind the prints, falling to `--wine-2` at the edges), light grain.
  The header floats over it, so the first screen is one field with no seam.
- **The sun comes out.** The window light (§6) fades up and slides into place
  over 1.9s; the eyebrow, name, line and buttons rise in after it, 90–120ms
  apart; the three prints settle onto the table last. Under 2s in all,
  `opacity`/`translate` only, off under `prefers-reduced-motion`.
- **Three prints on a table.** The hero photos are prints: a `--paper` border,
  a caption in Markazi in the bottom margin (like a hand-written label), each
  at its own small tilt (−1.4°, +3.4°, −4°), with a soft shadow below — the only
  blurred shadow on the site, because only here is there a table for a print
  to lie on. Hovering straightens and lifts one. On phones, one print.
- **The shelf strip.** Directly under the entrance, a gold band runs the eight
  section names past, divided by oxblood ◆, at 60s a loop. It pauses on hover;
  it is decorative (`aria-hidden`) because the real links are right below it.

---

## 6. The signature: the window light

Every photo shares one light source, a six-paned window in low sun. The page is
that room, so the window's light falls on the page too.

- An inline SVG: 2×3 panes skewed −32° (the lean of the shadows in the photos),
  blurred.
- **On cream** it is `--sun`, multiplied in — warm patches on paper.
  **On wine and teal** it is `--gold`, *screened* in — actual light, glowing on a
  wall in shade. This is why the entrance is dark: the signature only becomes
  light against shadow.
- The box is always exactly its parent's height and masked by an inscribed
  ellipse, so it fades to nothing before any edge. **If you can see where it
  stops, it is wrong.**
- Never on a product photo; the photo already has its own.

---

## 7. Space, radius, shadow, motion

- Spacing `--s-1`…`--s-6` = 8 / 16 / 24 / 40 / 64 / 104px. Gutter 16 / 32 / 48px.
- **One radius: 2px.** Chips are the one pill.
- **Shadows: exactly two kinds.** The hard gold offset (§3), and the print
  shadow (§5). Nothing else casts one.
- Every grid photo is **4:5**, cropped by `make_images.py` to where the object
  is; product pages show the uncropped photo.
- **Motion:** the entrance (once), the shelf strip (looping), the light drifting
  on section headers as you scroll, a 3.5% photo zoom on hover, view-transition
  cross-fades. All of it is off under `prefers-reduced-motion`.

---

## 8. Components

- **Card**: 4:5 photo, name (Markazi), price (`۳۵۰٬۰۰۰ تومان`), «قیمت روز» for
  silver, «قیمت را بپرسید» in `--gold-ink` for unpriced pieces.
- **Sold**: gathered at the foot of each section under «به خانهٔ تازه رفتند»,
  smaller, desaturated, unlinked — never deleted.
- **Order block**: the code, large; «کپی کد و نام» copies a ready-to-paste DM;
  one button per configured channel, the first in oxblood with the gold offset;
  "send to a friend" on phones.
- **Buy bar** (phones, product pages): price + «سفارش با کد S-10».
- **Chips**: section switcher on section pages; the current one is oxblood and
  scrolls itself into view on phones.
