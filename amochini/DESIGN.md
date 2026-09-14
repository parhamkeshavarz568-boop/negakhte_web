# DESIGN.md — عمو چینی / amochini.ir

The single source of truth for every visual decision on this site.
If a value you need is not in this file, **stop and ask for it to be added.**
Do not introduce a font, hex value, radius, shadow or spacing step silently.

---

## 1. Subject, audience, and the one job

**Subject.** The daily price of ASMCO brake parts — pads, discs and drums — for
Chinese-market cars in Iran. We are the main ASMCO supplier in the country, so
the catalogue is not a shop window, it is a **quotation**.

**Audience.** A mechanic or a parts-counter buyer in Tehran, standing in a
workshop, on a mid-range Android phone, on a slow connection, with one hand
free. They already know what part they need. They are checking one thing and
then making a phone call.

**The one job.** *Show today's number, say when it was taken, and show whether
it moved.* Everything else on the site exists to get someone to that number,
or to let them call about it.

The design consequence, stated once so it governs everything below: **this site
has no real product photography** — 130 products currently share four stock
images. A design that leads with product pictures would be a design built on a
lie. So this one leads with the figures, which are real, dated, and ours. The
photographs become supporting evidence, small and cropped, never the hero.

---

## 2. Colour — six named colours, unevenly weighted

Authored in OKLCH, shipped as hex. Hex is what ships because a meaningful share
of the audience is on Android WebView builds old enough to drop an `oklch()`
declaration entirely, and a dropped colour on this palette means black text on
a black board. The OKLCH value is the definition; the hex is the build output.

| Token | OKLCH | Hex | Role |
|---|---|---|---|
| `--board` | `oklch(0.200 0.014 70)` | `#1a150f` | **Dominant.** Warm near-black. The ground of the price board, the header, the footer, the tape. |
| `--paper` | `oklch(0.968 0.004 250)` | `#f2f5f7` | The reading ground. Faintly **cool**, never warm. |
| `--ink` | `oklch(0.255 0.008 70)` | `#25221f` | Text on paper. |
| `--amber` | `oklch(0.800 0.165 78)` | `#f7ae0c` | **The sharp accent.** Rationed. See the budget below. |
| `--rise` | `oklch(0.530 0.170 28)` | `#ba362e` | A price went **up** — bad news for someone buying a brake disc. |
| `--fall` | `oklch(0.515 0.160 250)` | `#0069be` | A price went **down**. |

### Derived siblings — the only permitted additions

Each exists because one ground cannot serve both a light and a dark surface.
There are no others.

| Token | OKLCH | Hex | Why it exists |
|---|---|---|---|
| `--board-2` | `oklch(0.265 0.014 70)` | `#2a241e` | Inset panels on the board. |
| `--rule-board` | `oklch(0.340 0.012 70)` | `#3c3731` | The hairline, on board. |
| `--paper-2` | `oklch(0.930 0.005 250)` | `#e5e8eb` | Image wells only. **Carries no text, ever.** |
| `--rule` | `oklch(0.855 0.006 250)` | `#ccd0d3` | The hairline, on paper. |
| `--rule-strong` | `oklch(0.600 0.006 250)` | `#7e8084` | Form-control borders. 3.61:1 on paper — WCAG 1.4.11. |
| `--ink-2` | `oklch(0.500 0.008 70)` | `#66625e` | Secondary text on paper. 5.52:1. |
| `--chalk` | `oklch(0.720 0.008 70)` | `#a8a49f` | Secondary text on board. 7.32:1. |
| `--rise-b` | `oklch(0.640 0.170 28)` | `#e15a4e` | `--rise`, lifted to read on board. |
| `--fall-b` | `oklch(0.660 0.140 250)` | `#4697e4` | `--fall`, lifted to read on board. |

**Six colours, fifteen tokens.** Down from 56 hex values and 20 rgba values.

### The weighting, stated as a budget

Not evenly weighted, and not left to chance:

- `--board` — **~55% of the pixels above the fold.** The board is the page.
- `--paper` — the remaining reading area, and nothing else.
- `--ink` / `--chalk` — all text.
- `--amber` — **at most 2% of any screen.** Its whole job is to mark *live*: the
  pulse dot on the tape, the today-stamp, the focus ring, the primary button,
  the active nav item. That is the complete list. Amber is never a section
  underline, never a heading colour, never a decorative rule. The previous
  build used it on five section headings in a row, which is exactly how an
  accent stops meaning anything.
- `--rise` doubles as the system's **single warning colour** — out of stock, the
  unavailable badge, the 404 number, the preview banner. That is not a second
  meaning smuggled in: for this reader a price rise and a shortage are the same
  news, so they get the same colour. `--fall` has no second job, and
  "in stock" is deliberately **uncoloured** (a plain ink square) — lending it
  `--fall` made "available" and "cheaper" the same blue.
- `--rise` / `--fall` — delta text and chart strokes only. **Never a surface**,
  and never a tinted chip ground: the four pale tint values the previous build
  used for that (`#fdeceb`, `#eaf2fb`, and two more) are gone. Area fills under
  a chart use the stroke colour at `fill-opacity`, so they add no new value.

### Colour is never the only signal

Every rise or fall also carries a glyph (▲ / ▼) and a signed number, so the
direction survives greyscale, CVD, forced-colors and a printout.

### Validated, not eyeballed

The diverging pair was run through `dataviz/scripts/validate_palette.js`:

- on paper `#ba362e` ↔ `#0069be` — ΔE **22.3** protan, **30.2** normal — ALL PASS
- on board `#e15a4e` ↔ `#4697e4` — ΔE **22.4** protan, **29.1** normal — ALL PASS

Note the polarity: this is the **inverse of a stock ticker**. A rising price is
bad for the person reading it, so the rise wears the warning colour. Blue is
not "good" the way green would be, which is another reason the glyph and the
word carry the meaning and the colour only reinforces it.

Red↔green was tested first and **failed** at ΔE 5.6 deutan. It is banned from
this palette permanently. Do not reintroduce it because it "reads as prices".

Every text pairing that ships was computed, not estimated. The full matrix is
in `docs/MEASUREMENTS.md`; the floor is 4.5:1 for text and 3:1 for controls.

---

## 3. Typefaces — two, and they do different jobs

### Display — **Lalezar** (Borna Izadpanah, SIL OFL 1.1)

Lalezar is a revival of the hand-painted lettering on mid-century Iranian shop
signs and street boards — it is named after a Tehran street. It is the literal
vernacular of the bazaar this business sells into, which is why it is here
rather than a display face chosen for looking sophisticated.

One weight (400), which for a display face of this density reads as black.
Used for: `h1`, section heads, the board's headline figure. **Never** for a
sentence, never below `--t-head`, never for a dense table.

### Body & figures — **Vazirmatn** (Saber Rastikerdar, SIL OFL 1.1)

The only Persian text face with a genuine variable 100–900 range, which is what
makes the weight extremes in §4 possible from a single file. A price board needs
a text face whose 800 is heavy enough to carry a number at 16px on a cheap LCD
and whose 200 is light enough to make a label recede completely — and it needs
both from the same skeleton so a figure and its label look related. Vazirmatn
does that; a static family cannot.

Tabular figures are on for every number in a column, so the digits align.

### Stacks — exactly two, and that is all

```css
--face-display: Lalezar, 'Vazirmatn fallback', Tahoma, sans-serif;
--face-text:    Vazirmatn, 'Vazirmatn fallback', Tahoma, sans-serif;
```

`system-ui` is **removed**. Both files are self-hosted and subset; neither is
fetched from a CDN, because Cloudflare and Google Fonts edges are unreliable
from inside Iran and a stalled font request holds up first paint.

### Banned, permanently

Inter. Roboto. Open Sans. System font stacks. Any serif paired with a warm
cream ground.

---

## 4. Type scale — five steps, 6.5× range

| Token | Size | Face | Weight | Used for |
|---|---|---|---|---|
| `--t-figure` | `clamp(48px, 13vw, 72px)` | Lalezar | 400 | The board's headline figure. One per page. |
| `--t-display` | `clamp(30px, 7vw, 44px)` | Lalezar | 400 | `h1` |
| `--t-head` | `24px` | Lalezar | 400 | Section heads, `h2`, `h3` |
| `--t-body` | `16px` | Vazirmatn | 400 | All prose |
| `--t-label` | `12px` | Vazirmatn | 400, tracked `+0.06em` | Labels, units, dates, table heads |

**12px → 72px is 6×.** The largest single jump is 24 → 44, which is 1.83×.

The label started at 11px at weight 200 and was **changed after looking at it**:
Vazirmatn ExtraLight at 11px in Persian is not readable on a 1× Android LCD,
which is the screen this site is actually read on. 12px at weight 400 is. The
200/800 extreme therefore lives at body size and above — the band's lede
paragraph at 200 against the figure — which is where it carries anyway.

Being straight about the brief: the instruction was 3×-plus jumps. The *range*
is 6.5×. The *steps* are not all 3×, and they must not be — a 3× jump down from
16px body text puts a label at 5px, which is unreadable on the phone this site
is built for. The drama comes from the gap between the figure and the label
(6.5×) sitting inside the same block, not from every rung of the ladder.

Five sizes total, down from 27 competing declarations. No raw `font-size`
anywhere; if a new size is needed, it gets added here first.

### Weight — the extremes, and nothing comfortable

**200 and 800.** Plus 400 for prose and for labels, because Persian below 400
at small sizes on a budget Android LCD is genuinely hard to read and this
audience is not browsing.

That is three weights. **500, 600 and 700 are banned** — those were 75 of the
previous build's 85 weight declarations, and a page where everything is
semi-bold has no emphasis at all.

Figures are 800. The lede paragraph is 200. Everything else is 400.

### Leading

Persian needs more than Latin. Prose `1.85`. Heads `1.2`. Figures `1`.

---

## 5. Spacing rhythm — five steps, each a real jump

```
--s1: 4px    hairline gaps, icon-to-text
--s2: 12px   inside a control, between a figure and its label
--s3: 24px   between rows, inside a panel
--s4: 48px   between blocks, and the section rhythm on phone
--s5: 96px   the section rhythm from 768px up
```

×3, ×2, ×2, ×2. Nothing between them. No raw padding or margin values — the
previous build had 12 different block-spacing declarations, half of them raw,
which is why the page had no beat.

**The section rule, no exceptions:** every top-level section is separated by
`--s4` on phone and `--s5` from 768px up. Nothing gets a custom gap because it
"needs a bit more room."

---

## 6. Radius rule

**2px. Everywhere. Or a pill, on something that is actually a pill.**

```
--r: 2px
--r-pill: 999px
```

A price board is cut card and printed rule. 12px and 16px soft corners are the
single loudest "generic web card" signal, and the previous build had five radius
tokens plus two raw values to choose between. Now there is one answer.

`50%` is permitted on one thing only: the live pulse dot — which appears
twice, on the tape's tag and on the board's date stamp, because it is the same
element doing the same job. A stock indicator is a square marker, not a dot.

---

## 7. Shadow rule

**There are no shadows.**

Depth is carried by **ground change** — board against paper — and by a **1px
rule**. That is the whole elevation system, and it is what a real board does:
ink, card, and a printed line.

The one exception is not decoration: the focus ring.

```
--focus: 0 0 0 3px var(--amber), 0 0 0 5px var(--board);
```

Two rings, so it stays visible against both grounds. This is the only
`box-shadow` value in the stylesheet, replacing seven, plus three one-off
`text-shadow` declarations that are all deleted.

---

## 8. The ONE signature element — **the board**

A full-bleed dark band of today's prices, with the date stamped on it.

It is the thing this site is remembered by, and the rules that make it that:

- It is **always full-bleed** — it breaks the 1180px column on every page. In
  the previous build, 26 of 31 sections sat in that same centred lane, and the
  board was one of them.
- It is **always the darkest thing on the screen.**
- Its figures are **the largest type on the page** — nothing else may use
  `--t-figure`.
- It carries **a date**, always, in amber. An undated price is a rumour.
- It appears **once per page.** On the home page it *is* the hero: there is no
  photographic hero above it any more. On a product page it holds that product's
  own price and history. On a category page, that category's movers.
- Nothing else on the site may be dark. If a second dark band appears, the
  signature is gone.

### The card formula is dissolved

Eleven components previously shared one white-rounded-bordered-shadowed
formula. There are now three surface families and nothing else:

1. **Board** — dark ground, no border, no radius. Prices, tape, header, footer.
2. **Panel** — paper ground, a 1px `--rule` top border only, `--r` 2px, no
   shadow. Structural content: filters, FAQ, specs, contact.
3. **Row** — no ground at all. A 1px `--rule` bottom border and nothing else.
   Product listings, brand lists, category lists, search suggestions.

A product listing is a **row**, not a card. That single change removes the
"identical rounded cards" read at its source.

---

## 9. One motion moment — the tape

**The tape scrolls, and the site has one pulse. Nothing else moves.**

Two expressions of one motion idea — the heartbeat — on one keyframe:

- `ticker-slide` — the tape's continuous crawl.
- `tick-pulse` — a 2.4s breath, used by the tape's dot, the board's date stamp,
  and the headlight glow (§14.4). Three elements, **one keyframe**. Adding a
  second pulse rhythm would make it two motion moments; reusing this one keeps
  it one.

One continuous horizontal crawl of today's prices, at the top of the page,
entering from the right where a Persian reader's eye starts. It is the site
saying *these numbers are live* in the only way a static page can.

Explicitly deleted, and not to be reintroduced:

- hover lift + shadow change on cards — **10 selectors, all removed**
- fade-and-slide-up section reveals — already removed once, for a real reason:
  they left the first four cards at `opacity: 0` for anyone who landed mid-page
- every other transition on every other element

The tape pauses on hover and on keyboard focus. Under
`prefers-reduced-motion: reduce` the animation is dropped entirely and it
becomes a plain horizontally scrollable strip with every item reachable — not a
frozen strip showing three of twenty.

---

## 10. Copy rules

Real copy, written for this audience. No "innovative solutions", no filler, no
adjectives doing a number's job.

- Prices are dated. Always. «قیمت روز ۲۳ شهریور» beats «قیمت روز».
- A price we do not have is «استعلام تلفنی», never «تماس بگیرید» alone and never
  a fabricated figure.
- A price history with fewer than two observations renders **nothing** — no
  chart, no "no change", no placeholder. This is a hard rule in `prices.py` and
  it stays one.
- No arrows appended to link or button text. The previous build had four
  «... ›». A link is already a link.
- No tracked-out ALL-CAPS eyebrow labels above headings.
- No 01/02/03 markers unless the content is genuinely a numbered sequence.

---

## 11. Every component ships its real states

Not a later pass. Default, **loading**, **empty**, **error**, **long text** —
and the mobile reflow built at the same time, not after.

Because this is a static build, "loading" and "error" are specific things:

| State | What it means here |
|---|---|
| **default** | has data |
| **loading** | the font has not landed → metric-matched fallback holds the box, so nothing reflows |
| **empty** | no price yet, no history yet, a filter matching nothing → a real sentence, never a blank box or a zero |
| **error** | JS off or failed → every slider, filter and suggestion list degrades to working HTML. The tape becomes a scrollable strip; the slider becomes a native scroller; the filter shows all rows |
| **long text** | Persian product names run to 60+ characters. Every name box is tested at its longest real value, not a short one |

### Non-negotiable, on every change

- Semantic HTML. A table of prices is a `<table>` with `<th scope>` and a
  `<caption>`.
- `:focus-visible` visible on every interactive element, using `--focus`.
- An accessible name on every icon button.
- AA contrast, computed against the actual ground, not assumed.
- `prefers-reduced-motion: reduce` respected.
- Latin runs inside Persian wrapped in `<bdi>`.
- Numbers: Persian digits for display, `U+066C` thousands, `U+066B` decimal, and
  a `<data value>` with Latin digits underneath for machines.

---

## 12. Before anything is called done

Screenshot at **375px**, **768px** and **1440px**. Look at the screenshots.
Write down what is actually wrong — spacing rhythm, alignment, overflow,
contrast, focus states — fix it, and re-screenshot to prove the fix.

Not done on the strength of the code.

---

## 13. Self-check: would this plan fit any similar brief?

Asked honestly, the first draft of this document would have. Here is what was
in it, and what it was replaced with.

**1. Warm cream paper, a serif display face, an amber accent.**
That is the default "trustworthy local business" move, and it is item eight on
the banned list. Worse, the previous build's page ground was already `#f4f2ef`
— three values per channel from the banned `#F4F1EA`. **Changed:** the paper is
now faintly *cool* (`oklch(... 250)` hue) so it can never read as cream, and the
display face is a Persian street-sign revival rather than any serif. The warm
tint moved to the near-black, where it does something — it keeps the board from
looking like a screen.

**2. A photographic hero with a headline over it.**
Kept from the draft out of habit. But this site has four stock photos for 130
products and its subject is *numbers*. A photo hero would have been the most
prominent dishonest thing on the page. **Changed:** the hero is gone. The board
is the hero. The constraint became the concept instead of a thing to hide.

**3. A five-step radius scale and a four-step shadow scale, "for hierarchy."**
This is the default answer and it is why every AI build looks the same.
**Changed:** no shadows at all, one radius. Hierarchy is carried by ground
change, which costs nothing and is what the real-world object does.

**4. Red for down, green for up.**
The obvious choice. It was measured and it **failed** — ΔE 5.6 deutan, below
even the 6–8 floor. **Changed:** red↔blue, validated at ΔE 22.3.

**5. Estedad as the display face.**
Another low-contrast Arabic sans. Pairing it with Vazirmatn is a weight change
dressed up as a voice change. **Changed:** Lalezar — a different *kind* of
letter, and one with an actual argument for being on this site.

**6. An amber underline under every section heading.**
Inherited from the previous build, where it appeared under five consecutive
headings. An accent used everywhere is not an accent. **Changed:** amber is
rationed to a 2%-of-screen budget with a closed list of permitted uses.

**7. A type scale from 13px to 38px.**
2.9×, every step ~1.2×, so nothing was ever dramatic. **Changed:** 11px to
72px, five steps, with weight 200 against weight 800 in the same block.

---

## 14. Named exceptions

The system is closed. Anything added after it was locked is recorded here, with
what it is, why, and what rule it bends. If it is not in this list and not in
§2–§9, it does not exist.

### 14.1 — Row-fill hover on a product row

```css
.card:hover{background:var(--paper-2)}
```

**Bends:** §9's "nothing else on this site moves" and the standing ban on
"hover transitions on every card".

**Why it is allowed:** it is not motion and it is not a transition. There is no
`transition`, no `transform`, no shadow and no scale — the row's ground changes
from `--paper` to `--paper-2` instantly, the way a table row highlights. It
introduces **no new value**: both are existing tokens.

**Why it is needed:** the fifteen-item scroller and the seventy-seven-row
category lattice gave a pointer user no feedback at all about what was
clickable. The underline on the product name (which is still there) only
appears once the cursor is on the text itself, not on the row.

### 14.2 — A 4px progress rail

The slider's progress rail goes from 2px to `--s1` (4px), `--rule` track with
an `--ink` fill.

**Bends:** nothing. 4px is an existing spacing token; no new value.

**Why it is needed:** at 2px the rail was measurably present and practically
invisible, which made the one affordance that tells a reader how far through a
fifteen-item scroller they are useless.

**Explicitly NOT amber.** An amber rail was offered and is declined. §2 rations
`--amber` to *live* signals — the pulse dot, the date stamp, the primary
button, the focus ring, the active nav item. A scroll-position indicator is not
a live signal, and spending the accent on it is exactly how the previous build
ended up with an accent that meant nothing.

### 14.3 — Slider rows are wider than grid rows

`flex-basis` goes from 266px to 340px on desktop, `clamp(260px, 78vw, 340px)`
below.

**Bends:** nothing — a component dimension, like the 1180px column.

**Why it is needed:** the reason the slider read as thin was not that it lacked
effects. It was that a 266px row gives a photograph a 266×200 box, which is too
small for a brake disc to land. At 340px the photo is 340×255 and three and a
half rows fill a 1440px screen instead of four and a third. The slider gets its
own `sizes` attribute rather than sharing the grid's, so the grid does not
start over-fetching a 700px rendition for a 283px box.

**The cost, stated:** the three disc photographs are 700×700 sources, so the 80
disc products get a genuinely sharper image in the wider box. `cat-brake-pads`
is a 400×400 source — that is the real file, not a setting — so the 50 pad
products are now 1.7× short of a DPR-2 340px box instead of 1.4× short of a
283px one. They were already capped; they are slightly softer now. Upscaling
would be fake sharpness, so it is not done. This is the photography ceiling in
`docs/PLACEHOLDERS.md` showing up again, and real product photography is what
fixes it.

### 14.4 — The headlights

A 1200×200 crop of a supplied photograph — two amber headlight clusters
glowing in pure black — closing the board band, full-bleed, once per page.

**Bends:** §8's "nothing else on the site may be dark" and §9's "nothing else
moves". Both narrowly, and both on purpose.

**Why it is allowed.**

It is not a second dark band. It sits *inside* `<section class="board-band">`,
outside the 1180px `.wrap`, and `.bb-lit` removes the section's bottom padding
so the photograph **is** the board's bottom edge. The board still ends once,
and now it ends in headlights.

The photograph is static. The only thing that animates is the **opacity** of
two radial glows over the lamps, and it animates on `tick-pulse` — the same
keyframe and the same 2.4s rhythm as the tape's dot and the date stamp. One
motion idea, three places, as §9 now records. A second rhythm would have made
it two moments; this does not.

It introduces **no new colour**: the glow is `var(--amber)` to `transparent`,
and its strength comes from one static `opacity` on the wrapper, so the
gradient needs no alpha and the stylesheet still carries no `rgba()`.

**Why this image, and not the other four supplied.**

The amber matches `--amber` and the ground matches `--board`, which is luck
worth taking. More importantly it is the only one of the five that is **on
subject and anonymous**: no car body, no badge, no manufacturer's mark — two
lights in the dark, which is what a brake-parts shop is about. The other four
are a BMW M3 in daylight, a BMW front end, a Dodge Challenger rear in red
smoke and a Challenger burnout. All four show recognisable cars that this shop
does not sell parts for, three carry other manufacturers' trademarks, and a
mechanic looking for لنت ترمز for an MVM 315 learns nothing from a Hellcat.
They are vendored at `build/original/images/supplied/` and unused.

**Engineering notes.**

- The crop is measured, not eyeballed: the bright band sits at y 606–689 of
  the 900px original, so the window is y 560–760.
- The glow centres are the measured lamp centres — x 185 and x 1036 of 1200,
  i.e. 15.4% and 86.3% — set with **physical `left`**, because they must not
  flip with text direction.
- `aspect-ratio: 6/1` matches the source at every width, so `cover` never has
  anything to crop. A 4:1 phone variant was tried and rejected: it scaled to
  the height and took 25% off each side, cutting both lamps in half, since the
  lamps sit exactly where a horizontal crop bites.
- Opacity is compositor-only. An animated `filter: brightness()` on a 1200px
  photograph would repaint every frame; this does not.
- Under `prefers-reduced-motion` the global rule freezes the animation at its
  base state, which leaves the lamps simply **on**. That is the right still.
- 5.0 KB as AVIF at 1200px, 2.6 KB at 640. Heaviest page went 141.2 → 141.5 KB
  against the 150 KB budget, and CLS stayed 0.000 on all 24 combinations —
  the `aspect-ratio` plus the `width`/`height` attributes reserve the box.
- The image is decorative, so `alt=""` and `aria-hidden="true"`: it carries no
  information a screen-reader user would miss.
