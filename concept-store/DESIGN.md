# DESIGN.md — the concept store

The single source of truth for every visual decision. If a value you need is
not here, add it here first, then use it. `build/assets/site.css` implements
this file; `validate.py` checks every text/ground pair on every build.

The approved board this was built from:
https://claude.ai/artifact/12raGgd4jreCxTZ9R4C3Nx

---

## 1. Subject, audience, the one job

**Subject.** A small Iranian concept store: Ayshid's handmade candles, glazed
ceramics, crochet flowers, silver, Nixgel / Niura / ELORA beauty, incense,
spices, 3D stickers and postcards. Many pieces are one-offs.

**Audience.** Someone on their phone, usually arriving from Instagram or a link
a friend sent, looking for a gift or something for their own shelf.

**The one job.** *Let someone fall for a piece, then send its code.* No cart:
every piece has a code (`S-10`) and every product page ends in the shop's DM.

**The consequences.**
- The product photography is excellent and uniform, so **photographs carry the
  page** and colour stays out of their way: almost all paper and photograph.
- The shop belongs to the same house as **negakhte** and should feel related
  through colour and a few small marks, without saying so anywhere.

---

## 2. Colour: negakhte's palette, in small doses

| Token | Hex | From | Role |
|---|---|---|---|
| `--paper` | `#F5EFE6` | negakhte | **The page.** About 70% of any screen. |
| `--stone` | `#EAE0D1` | ours | Panels (statement, chat), photo wells. |
| `--ink` | `#1F1A15` | negakhte | Text; the footer. 15.1:1 on paper. |
| `--ink-2` | `#6C6255` | negakhte | Secondary text. 5.2:1 on paper, 4.6:1 on stone. |
| `--rule` | `#DDD1BF` | ours | Hairlines. Carries no text. |
| `--ox` | `#7A2E1F` | negakhte | **Oxblood, about 2%:** the heavy word in a headline, primary buttons, the current tab, link text. 8.2:1. |
| `--ox-deep` | `#5A1F12` | negakhte | Hover. |
| `--gold` | `#C99846` | negakhte | **Marks only, under 1%:** the ◆, the highlighter, the button shadow. Never text on paper. |
| `--gold-ink` | `#7E5D25` | negakhte | Gold that carries small text on paper (eyebrows, "ask for price"). 5.3:1. |
| `--on-ink` | `#D8CFC3` | ours | Secondary text on the ink footer. 11.6:1. |

**Removed in this version:** the wine fields, the teal band, the gold shelf
strip. Only one dark block remains: the footer, in ink.

**Text on photographs.** The home hero sets ink straight onto the photo's calm
wall, and the eyebrow there is ink too: gold disappears on beige.

---

## 3. Type: Estedad, one family

**Estedad** (Amin Abedi, OFL), variable 100–900, self-hosted as one 49 KB
subset. It was chosen after setting nine Persian faces side by side on the real
headline. One family removes the clash the previous two-typeface pairing had;
the contrast comes from weight instead.

| Token | Size | Weight | Use |
|---|---|---|---|
| `--t-title` | 64–152px | Thin 200 | one-word section titles («شمع.») |
| `--t-h1` | 52–104px | Thin 200 | the home headline; long page titles (`h1.long`) |
| `--t-h2` | 34–56px | Thin 200 | section heads |
| `--t-h3` | 24px | SemiBold 600 | step titles |
| `--t-lede` | 18px | Regular 400 | intros |
| `--t-name` | 17px | Medium 500 | product names on cards |
| `--t-body` | 15px | Regular 400 | text, UI |
| `--t-meta` | 13px | Medium 500 | eyebrows, labels |

- **The headline treatment:** Thin 200 with one word in Black 800 oxblood,
  sitting on a thin gold highlighter («چیزهای کوچکِ **دست‌ساز**»). It's negakhte's
  own headline device, set in a different face.
- **Numerals** are Persian (`۴۶۸٬۰۰۰`). Prices use proportional figures:
  tabular figures give the separator `٬` a full digit width (`۵۷۰ , ۰۰۰`).
- **Codes** stay Latin and LTR (`S-10`), SemiBold, tracked: they are what
  people type into a DM.

---

## 4. The marks shared with negakhte

| Mark | here |
|---|---|
| **◆** a small gold square at 45° | after the shop's name, in the header and the giant footer name |
| **The highlighter** — a thin gold bar low under the words | under the heavy word of the home headline; «تازه» in «به خانهٔ تازه رفتند» |
| **The offset shadow** — hard 4px gold, no blur; lifts on hover | every primary button, and the phone buy bar |
| **The ornament eyebrow** — a 2rem rule, then small text | above every headline |

---

## 5. Images: two kinds, never mixed up

1. **Product photographs** (`build/original/photos/`): the shop's own photos
   and the **only** images of anything for sale. Grid tiles are a
   subject-aware 4:5 crop; product pages show the uncropped photo.
2. **Mood images** (`build/original/atmosphere/`, see its MANIFEST): seven
   generated images of the same corner, light and materials, with nothing for
   sale in them. They are the home hero (wide; tall on phones), the statement
   image, and the section banners. They are decorative (`alt=""`, in a
   `<picture class="deco">`, which the validator requires for an empty alt).

| Mood image | Used for |
|---|---|
| `hero-wide` / `hero-tall` | home hero (desktop / phone); beauty, spices, small-gifts banners; 404 |
| `light-ledge` | home statement; incense banner; about |
| `candles`, `ceramics`, `crochet`, `silver` | those sections' banners |

---

## 6. The pages

**Home**
1. **The sunlit corner.** The empty corner every product was photographed in,
   full-bleed. The header floats over it. The headline sits on the calm wall
   (right, as Persian reads), and the three real numbers rest on the stone
   ledge. On phones a tall version of the same corner.
2. **The vitrine.** Eight collections as tall photos edge to edge. Desktop with
   a mouse: the first pane is open; the one under the pointer widens (flex
   3.1×, 0.7s), closed panes are slightly desaturated with small labels.
   Touch and narrow screens: a sideways swipe, 76vw panes (42vw on tablets).
3. **The shelf.** Ten pieces in a magazine rhythm on a 12-column grid: one big
   (6 columns × 2 rows) beside four small, then mirrored. Code, name and price
   under each.
4. **The statement.** The light-on-stone image beside «با دست، **یکی‌یکی.**»
   and three live counts.
5. **Ordering.** Three steps with thin oxblood numerals, beside the actual
   message a customer sends (a sample chat bubble).
6. **Footer.** Ink. Columns, then the shop's name set Thin 100 at up to 240px.

**Section page.** Eyebrow, the one-word title huge and thin with an oxblood
full stop, intro, counts; the section's mood banner beside it (below it on
phones); tabs for all eight sections; a 4/3/2-column grid; sold pieces at the
foot in grey under «به خانهٔ تازه رفتند».

**Product page.** The photo runs to the window edge at full height, uncropped;
beside it (sticky): crumbs, section, name in Thin, price, the code in its own
box with «کپی کد و نام», one button per channel (the first oxblood with the
gold shadow), notes with gold ◆ bullets. Phones: a buy bar pinned to the bottom.

---

## 7. Space, radius, shadow, motion

- Spacing `--s1`…`--s6` = 8 / 16 / 24 / 40 / 64 / 112px. Gutter 18 / 32 / 48px.
  Content width 1440px; the hero, vitrine, statement and footer bleed full width.
- **One radius: 2px.** The chat bubble is the one rounded shape: it's a chat bubble.
- **Shadows: the gold offset only**, plus the menu dropdown's soft shadow.
- **Motion, each once and quiet:** the hero photo settles (scale 1.06 → 1,
  2.6s) while the headline lines rise; vitrine panes unveil from the bottom as
  they scroll into view (scroll-driven, where supported); the pane widening;
  a 3.5% photo zoom on hover; view-transition cross-fades. All of it is off
  under `prefers-reduced-motion`, and nothing is hidden at rest.
