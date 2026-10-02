# DESIGN.md — the concept store

The single source of truth for every visual decision. If a value you need is
not here, add it here first, then use it. `build/assets/site.css` implements
this file; `validate.py` checks every text/ground pair on every build.

The approved board this was built from:
https://claude.ai/artifact/12raGgd4jreCxTZ9R4C3Nx

---

## 1. Subject, audience, the one job

**Subject.** A small Iranian concept store: candles, glazed ceramics, crochet
flowers, silver, Nixgel / Niura / ELORA beauty, incense, spices, stickers and
postcards — and **whatever a customer asks for**: the shop sources on request.
It is *not* a handmade store, and nothing on the site should position it as one.

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

## 3. Type: Vazirmatn, one family, sturdy weights

**Vazirmatn** (Saber Rastikerdar, OFL), variable 100–900, self-hosted as one
56 KB subset: negakhte's own typeface, the pinned v33.003 amochini vendors.

Two earlier choices failed in front of the owner, and the reasons are rules now:
- **Nothing lighter than 400.** Thin Persian at display sizes looks fragile
  and the joins look broken (Estedad Thin, rejected).
- **Emphasis is colour, never a jump in weight.** A Thin headline with one
  Black word reads as two fonts that don't match. The key word is the same
  weight, in oxblood, on the gold highlighter, exactly negakhte's device.
- **No negative letter-spacing** on Persian: tightening joined script makes
  letters collide.
- One family only (a second display face, Markazi, clashed with the text).

| Token | Size | Weight | Use |
|---|---|---|---|
| `--t-title` | 52–108px | Bold 700 | one-word section titles («شمع.») |
| `--t-h1` | 48–92px | Bold 700 (word 800) | the home headline; long page titles (`h1.long`) |
| `--t-h2` | 30–46px | Bold 700 | section heads |
| `--t-h3` | 24px | SemiBold 600 | step titles |
| `--t-lede` | 18px | Regular 400 | intros |
| `--t-name` | 17px | Medium 500 | product names on cards |
| `--t-body` | 15px | Regular 400 | text, UI |
| `--t-meta` | 13px | Medium 500 | eyebrows, labels |

Headlines read `--display`, `--w-display` and `--w-strong`, so the face can
be swapped in two lines. Numerals are Persian (`۴۶۸٬۰۰۰`), proportional (tabular
figures give `٬` a full digit width). Codes stay Latin and LTR (`S-10`).

---

## 3b. Voice

- **Speak to one person, in the singular (تو).** Never the formal plural
  (شما · بفرستید · بگویید), which reads like a book or a bank.
- **Warm and lightly conversational, written not spoken:** «کدش رو بفرست»،
  «اگه تو ویترین نبود، فقط بگو چی می‌خوای». Polite, never slangy.
- **The shop finds what you ask for.** Never call it a handmade store.
- Literary register only where it is literature: the verse.

---

## 4. The marks shared with negakhte

| Mark | here |
|---|---|
| **◆** a small gold square at 45° | after the shop's name, in the header and the giant footer name |
| **The highlighter** — a gold bar across the lower part of the word | under «دو هزار کوزه» in the home verse; «تازه» in «به خانهٔ تازه رفتند» |
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
1. **The sunlit corner.** The empty corner the products were photographed in,
   full-bleed, the header floating over it. On its calm wall: a classical verse
   instead of a slogan, one of 15 chosen at random on every load (never the
   same twice in a row), the poet's name beneath, one line of intro,
   «دیدن ویترین» and «سفارش ویژه», and two numbers on the stone ledge.
   - The verses (`site_config.HERO`): Khayyam ×4, Hafez ×5, Molavi ×3,
     Saadi ×2, Rudaki ×1, picked for the shop's world (objects, a welcome,
     seeking, scent, light, the moment). **Every one is checked against
     Ganjoor and given in its exact text with its source**; validate.py
     refuses one without. Three were misremembered before checking, and one
     common "Hafez" line turned out to be only attributed to him.
   - A small inline script picks the verse before the first paint, so it
     never flickers and the entrance animates it. It sizes the verse so each
     misra stays on one line; on a narrow phone a long misra splits into two
     balanced halves rather than going below 22px. No JavaScript: the
     Khayyam verse, the first in the list.
2. **The vitrine.** Eight collections as tall photos edge to edge. Desktop with
   a mouse: the first pane is open; the one under the pointer widens (flex
   3.1×, 0.7s), closed panes are slightly desaturated with small labels.
   Touch and narrow screens: a sideways swipe, 76vw panes (42vw on tablets).
3. **The shelf.** Ten pieces in a magazine rhythm on a 12-column grid: one big
   (6 columns × 2 rows) beside four small, then mirrored. Code, name and price
   under each.
4. **Special order.** The light-on-stone image beside «دنبال چیز **خاصی** هستی؟»:
   if it isn't in the vitrine, say what you want and the shop finds it. With the
   order buttons (WhatsApp prefilled «سلام! دنبال اینم:»).
5. **Ordering.** Three steps with thin oxblood numerals, beside the actual
   message a customer sends (a sample chat bubble).
6. **Footer.** Ink. Columns, then the shop's name set Black 800, very large.

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
- **The entrance, once per visit (about 1.6s):** the photo brightens and
  settles (scale 1.035 → 1, 3.2s, ease-out); one faint sunbeam passes over the
  wall; the headline arrives word by word, each rising out of a slight blur
  (70ms apart); the highlighter then draws under «دو هزار کوزه»; the poet's
  name, intro, buttons and numbers follow. Deliberately quiet, never shiny.
- **The one thing that keeps moving:** a few specks of dust drifting in the
  window light (site.js; 18–48 specks, paused off-screen and in hidden tabs).
- Also: vitrine panes unveil as they scroll in, the pane widening, a 3.5% photo
  zoom on hover, view-transition cross-fades. All of it is off under
  `prefers-reduced-motion`, and nothing is hidden at rest.
