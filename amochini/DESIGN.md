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
- `tick-pulse` — a 2.4s breath, used by the tape's dot and the board's date
  stamp. Two elements, **one keyframe**. Adding a second pulse rhythm would
  make it two motion moments; reusing this one keeps it one.

  It had a third user — a glow pulsing over a pair of CSS-drawn headlights at
  the foot of the board. §14.4 replaced that construction with a photograph,
  so the board now has **no moving parts at all** and the tape carries the
  whole motion budget on its own. That is the better version of this rule, and
  it arrived by deleting something rather than by adding to it.

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

### 14.4 — The board's photograph

The shop's own still life — its boxes, a brake disc, caliper, pad set,
filters, battery, belt, plugs and a headlight on a wet floor, already lit
black-and-amber — **opening** the board band, full-bleed, once per page, on
the home page only.

**Bends:** §8's "nothing else on the site may be dark", and §1's refusal of a
photographic hero.

**Why it is allowed.**

It is not a second dark band. It sits *inside* `<section class="board-band">`,
outside the 1180px `.wrap`, and `.bb-lit` removes the section's top padding so
the photograph **is** the board's leading edge. The board still begins once.

It is not a hero either, and the distinction is the whole argument. A hero
sits *behind* the words and asks the reader to look past it. This sits
*above* them, in its own register, and stops. The page's headline is still a
number — `--t-figure`, one per page, a real measured price with a real product
attached — and the photograph never competes with it for the same pixels. What
it does is answer, in the first 170 pixels, a question the text needs a
paragraph for: what trade is this?

**Three frames stood here. Only the third is the shop's.**

1. A dim crop of amber headlights under a pair of CSS-drawn radial glows.
   Three stacked gradients read as a glow effect *painted onto* a photograph
   rather than as light *in* one, and the crop underneath was soft.
2. A stock Dodge Challenger, rear, in red smoke. Better made, and the grading
   work on it (§14.4 as it read before) was sound — but it showed a car this
   shop sells no parts for and carried another manufacturer's wordmark, and
   the owner rejected it. The source is deleted.
3. This one, which is **theirs**: their wall, their boxes, their parts. That
   is the whole difference, and it is worth more than any amount of grading.
   A stock photograph can only ever be about cars in general; this one is
   about this shop.

**How it is cut** — `build/make_images.py:_board_band()`, run at build time
from the vendored source so the recipe stays reviewable:

1. **Crop** (0,380)–(1855,760) of the 1855×848 frame, 4.88∶1. The window
   excludes the **wall sign**, and that is the point: the sign reads
   «شماره عمو چینی» — *"Number Uncle Chinese"* — and the shop is «عمو چینی».
   It is the one piece of text in the frame big enough to read at band size,
   so cropping it out is cheaper and safer than retouching it. The ratio is
   also close to the band's own, so `cover` throws away little; the first cut
   was 4.03∶1 and desktop was discarding a third of every row it downloaded.
2. **Soften** the three package wordmarks. The same wrong string is printed
   small on a box, an oil filter and the battery, and those sit among the
   parts, so they survive the crop. Each is replaced by a **feathered**
   Gaussian of itself: the packaging keeps its amber-on-black lettering and
   its logo, and the words stop being words. Small print on a box is what
   this looks like, which is what packaging looks like anyway. The feather is
   not optional — a hard-edged blur leaves a rectangle that, at the width the
   band is shown, is more visible than the text was.
3. **Grade** on the same LUT as the frame before it, at much gentler settings:
   γ=1.25 and a 30% mix toward `--board`. The Challenger frame was a bright
   studio shot that needed γ=2.2 to become a dark band. This one arrives dark
   and already in the site's two colours, so heavy grading only muddies it.

**Engineering notes.**

- **Height, not `aspect-ratio`.** Honoured as a ratio, 4.88∶1 collapses to an
  81px sliver on a 375px phone — not an image, a rule.
  `height: clamp(170px, 17vw, 260px)` with `object-fit: cover` keeps the band
  the same visual weight at every width and crops instead. The floor was 150px
  under the previous frame and went to 170 for this one: a still life needs
  more room than a light signature, and 150/170/190 were compared on a phone
  before choosing. 190 pushed the figure too far down.
- The `17vw` middle term is not decoration. A **fixed** height was tried;
  measured at 1920 it had zoomed to a close-up, because with `cover` every
  extra pixel of width is paid for by cropping tighter.
- **A phone gets a different photograph, not a crop of this one.** Half of a
  group shot is a group shot with the ends cut off. The owner supplied a
  contact sheet of closer frames from the same shoot, and `board-band-sm` is
  the one that reads as a brake shop in a single glance: a slotted disc and a
  caliper. At 740×340 it is 2.18∶1 against the phone band's 2.2∶1, so there is
  almost nothing to crop, and 740 is exactly what a 375px band wants at DPR 2.
  It is also **smaller than the wide frame's phone rendition** — the phone
  gets a sharper, better-composed band for fewer bytes (138.9 → 137.1 KB).
  Switched with `<source media="(max-width:699px)">` in `picture(art=…)`.
- **In the close-up the sign could be fixed rather than hidden.** At that
  distance the two halves read apart: «شماره» is set in **white** and
  «عمو چینی» in amber. Removing only the white word leaves the shop's actual
  name, in its own colour, correctly spelled — the wall behind is flat unlit
  texture, cloned from 78px below. The wide frame had no such luck, which is
  why there the sign is cropped away instead.
- **`object-position: 32% 50%`** on the wide frame. Where it *is* cropped —
  tablets — the centred half is the oil filter and the air filter, a dark blur
  that says nothing about what this shop sells. The disc, caliper and pad set
  sit between 18% and 40%, so the crop is pulled onto them. Above ~1000px the
  band is wider in ratio than the photograph and `cover` crops vertically
  instead, where the x value does nothing, so this costs the desktop
  composition exactly nothing. It is switched back to 50% below 700px, where
  the close-up needs no steering.
- Capped at `max-width: 1600px`. Past that the widest rendition (1200px) is
  stretched more than a third and softens. Two
  `linear-gradient(var(--board), transparent)` seams over the outer 6% hide
  the join at the cap, and below it they act as a vignette that keeps the
  frame from ending on a hard bright edge.
- **The bottom dissolves into the board** — `mask-image` to `transparent` over
  the last 42% — and the board's text starts *inside* that fade, via
  `margin-block-end: calc(var(--bh) * -0.16)`. The headline reads as coming
  out of the photograph rather than sitting under a picture of it, and a phone
  gets ~27px of the fold back. Derived from `--bh`, not typed twice.
- Masks take an **alpha** channel, not a colour. The `#000` in that gradient
  is opacity, and is the one hex in the stylesheet outside the §2 token set.
- **Contrast is measured, not assumed.** `build/check_contrast.py` hides the
  band's text, screenshots the bare ground, and reads the brightest pixel
  inside each text box — an average, or the box's centre, would pass a
  headline whose last word sits on a chrome highlight. Worst case across
  375/768/1440/1920: **6.45∶1**, under the table heading at 1920. AA needs
  4.5. The margin is thinner than the smoke frame's 10.25 because this
  photograph has bright highlights where that one had none, which is exactly
  why the check exists.
- **Quality was chosen at the size it is shown.** 34→54 encoded at 1200px and
  then displayed the way the page displays them — a 1200px file downscaled
  into a 1440×245 box — because that downscale hides artefacts and judging
  the files at 1∶1 would have bought fidelity nobody can see. All four are
  indistinguishable, with no blocking in the pad texture or the floor
  reflections. q=38 is the cheapest with headroom, 13.1 KB.
- **This frame costs real bytes.** Most were found, one was conceded, and the
  difference is written down. Found: the crop (4.03∶1 → 4.88∶1, stop shipping
  rows `cover` discards); the quality, chosen as above; the art-directed phone
  frame; and the **weight axis** — Vazirmatn shipped `wght 100–900` while §4
  allows three weights and nothing on the site requests outside 200–800, so
  the subset is instanced to that range, 57.1 → 54.3 KB on **every page**.
  Conceded: the budget is now **per viewport** — mobile 150 KB, desktop 170 —
  because they were never the same constraint. 150 exists for an Iranian
  mobile connection and mobile still meets it with room (**137.1 KB**).
  Desktop at DPR 2 asks a 1440px band for a 2880px image and gets the full
  1855px rendition; those users are on fixed lines. **161.8 KB.** The next
  real saving is the other 73.9 KB of the base: two webfonts.
- **Renditions go to the source's own width, 1855px.** They were capped at
  1200 for one build, to fit a single shared byte budget, and the owner caught
  it in one look: *"the quality here is not really great, the image is
  blurry."* They were right — the band renders up to 1600 CSS px, so a 1200px
  file is stretched a third on a wide screen and much worse on a HiDPI one.
  **Saving 13 KB by shipping a visibly soft hero is not a saving**, and the
  budget was the thing that had to give.
- CLS **0.000** on all 24 page/viewport combinations — the declared height
  reserves the box before the image decodes.
- The image is decorative: `alt=""` and `aria-hidden="true"`. The headline
  immediately below says in words what it says in parts.

### 14.5 — The product row's hierarchy

Six things in a card body were within one step of each other, so the row had
no loudest element. Four changes, and one refusal.

**The price is now `--t-display`, not `--t-head`** — 30–44px against a 16px
title, a ratio of 2.75 instead of 1.5.

**It stays in the TEXT face.** Lalezar has no `tnum` feature and its Persian
digit advances run from 286 to 680 units — a 2.4× spread with no way to
equalise them — so a column of prices set in it cannot align across cards.
Vazirmatn has `tnum`. Alignment beats the display face here, and this is the
only place in the system where those two pull against each other.

**The trend chip drops to weight 400** in a product row. At 800 in a warning
colour it was the loudest pixel in the card, louder than the price it sat
under. It keeps weight 800 on the board and in the stat tiles, where the delta
*is* the subject.

**The title is clamped to two lines** and nothing in the body may be squeezed.
Measured: a 60-character name grew to three lines, and because the price is
pinned by `margin-top: auto` the row it pushed into had nothing to give — the
tag row shrank and the third line rendered on top of the part code. The
longest real title is 38 characters, 32 once the variant chip takes the code.

**The four facts in the tag row get four treatments**, because they were one
bordered chip each and so an identity, an attribute, a sub-brand and a machine
code all looked the same:

| fact | treatment | why |
|---|---|---|
| part code `AMO-081` | ink-2, no box | a machine string, not a label |
| car `ام‌وی‌ام` | ink, weight 800, no box | an identity |
| fitment `جلو` | ink-2 in a quiet box | an attribute you filter on |
| product line `TRA-X` | solid `--board`, paper text | a sub-brand, and a spec |

The product line also moved **off the photograph and into the row**. It used
to share one exclusive slot with the out-of-stock warning, so a stock warning
and a sub-brand wore one costume and a product could not be both.

**`--amber` on the carousel's CTA.** This widens §2: amber's permitted list
says "the primary button", and a card's order button is the card's primary
action. It is the carousel only — solid `--board` in the category grid, where
four amber buttons per row down 77 rows would be a wall of yellow. A grey
outlined button reads as disabled, which is what it was, and grey outlined
buttons are on the banned list.

### 14.6 — Latin runs inside Persian titles are isolated

`latin_bdi()` in `layout.py` escapes a title and wraps every Latin/digit run
in `<bdi>`. Applied to every rendered product name: the card, the `<h1>`, the
tape, the board's headline figure, both price tables and the stat tiles.

Not cosmetic. Under UAX#9 a Latin run inside RTL text resolves by its
surroundings, and the joiners are **bidi-neutral**: the `/` in
«برلیانس 220/230 عقب» and the `-` in «TRA-X» take direction from whatever sits
next to them, so a title can reorder depending on the words around it. That is
the same failure class that reached us in the source data as «230-220» and
«35 CS», which `build_catalog.py` repairs — this stops the build re-creating it
on the way out. A single run with no trailing neutral (`33X`, `315`) happens to
render correctly unisolated, which is why it was easy to miss.

`data-*` attributes keep the plain escaped form: they are read by `site.js`,
not rendered.

### 14.7 — Two things asked for and not done

**"Separate cards with whitespace, not borders and grey fills."** Declined.
The hairline lattice is §8, and it is the specific thing that replaced eleven
identical shadowed cards. Whitespace separation is what the generic build
looked like. Available on request as a further exception, but it is a step
back.

**"Unify the product images — pick ONE treatment."** Cannot be done in code.
Three of the four photographs are 700×700 white-studio shots and the fourth,
which 50 of 130 products share, is a 400×400 dark-ground shot. `object-fit:
cover` fills the box, so the well colour never shows and the clash is between
the photographs' own backgrounds. A `filter` would flatten real product
colour, and upscaling would be fake detail. This is the photography ceiling in
`docs/PLACEHOLDERS.md` and it is the highest-value thing the owner can fix.

**Also corrected while here:** the card photograph now carries `alt=""`. The
product name sits immediately beside it, so the old `alt="{title}"` made a
screen reader announce each product twice — and the same stock image is shared
by up to 50 products, so an alt claiming to be one specific part was a small
lie. The product page's gallery keeps a real alt.

### 14.8 — The real mark

An amber gear ring around a white curly head with a moustache — عمو چینی,
"Chinese Uncle". Supplied by the owner inside a promotional poster, so
`build/make_icons.py` carries the crop and the colour key and everything
rebuilds from the file he sent.

**Bends:** nothing. Its amber is within a hair of `--amber` and its white
within a hair of `--paper`, so the mark repaints to those two exactly and adds
no value to the palette.

**Why it is repainted rather than lifted.** The poster gives the gear a 3D drop
shadow. A luminance key left a muddy brown fringe around it, and §7 says this
system has no shadows — so the key classifies in HSV and repaints flat
`--amber` and `--paper`. The mark comes out as two flat inks on transparency,
which is what it should have been.

**Shipped as lossless WebP with a palettised PNG fallback, and deliberately no
AVIF.** Measured at 140px: 1.5 KB lossless WebP, 2.3 KB PNG8, against 5.6 KB
AVIF from the RGBA source. AVIF's transform coding is the wrong tool for
hard-edged flat art. The mark is on all 155 pages, so the difference is about
4 KB a page — which is what brought the home page back under the 150 KB budget
after it first went to 150.8.

**The wordmark stays as text** beside it. The link needs an accessible name,
the brand needs to be selectable and searchable, and the mark carries `alt=""`
because the name is right there.
