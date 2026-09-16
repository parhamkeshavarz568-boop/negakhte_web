# نگاخته — طرح دیزاین
# Negakhte — Design Plan

**Property:** the self-knowledge tests site (`negakhte_main`)
**Author:** design lead
**Status:** approved direction, phased implementation
**Sibling property:** کافه نگاخته (`ali-optimized/`) — the brand's other site

---

## 0. Brief

### 0.1 What this document is

The governing contract for how this site looks and behaves. Every colour, every
type size, every ornament and every component state is specified here. If the
code and this document disagree, one of them is a bug.

Nothing gets added to the stylesheet that is not in §2. No new hex value, no new
font, no new radius, no new shadow — not silently. Adding one means adding it
here first, as a named token with a reason.

### 0.2 The goal, stated plainly

Make the site **appealing enough that a stranger who lands on it wants to take a
test, and wants to send it to a friend.** That is the whole commercial objective.
Everything below serves it.

The mechanics are already sound — routing, persistence, keyboard access, tie
handling, contrast, a 38 KB self-hosted font. What the site does not have is a
reason to care. It looks like a form. It should look like something made.

### 0.3 Who is on the other side of the screen

- Persian-reading, overwhelmingly on a phone, arriving from Instagram or a
  Telegram forward.
- Came for one thing: to find out something about themselves.
- Will decide in about two seconds whether this is worth seventy questions.
- Has seen a hundred quiz sites. Has not seen one that looks like a Persian
  manuscript.
- On a network where a third-party font request may simply never resolve.

The second-order audience is the friend they forward it to. That makes the
result screen and the share card product surfaces, not afterthoughts.

### 0.4 What success looks like

| | Now | Target |
|---|---|---|
| A stranger can tell what this is in 2s | no front door at all — lands on a list | a landing screen that states it in one line |
| Reason to prefer this over any other quiz site | none | the هفت خان frame; nothing else looks like it |
| Result worth screenshotting | a bar chart | a sealed مُهر with your figure's name on it |
| Share preview | one generic card for all seven tests | a per-test card |
| Visual relationship to کافه نگاخته | none | visibly the same house |

---

## 1. The idea: هفت خان

### 1.1 Where it comes from — not invented here

The brand already has an identity, and it is a good one. کافه نگاخته's about
page is not a page; it is a **دفتر تذکره** — a manuscript register, written in
classical register with a دیباچه, a فهرستِ ابواب, and numbered باب chapters. Its
declared chapters are:

- در بیانِ نشانِ کافه — the meaning of the mark
- در گردشِ افلاک و سیرِ مهر و ماه — the turning of the heavens
- در شرحِ دوازده برجِ آسمان — the twelve towers of the sky
- در آن قلمِ سحرآمیز که نام می‌نگارد — the pen that inscribes the name
- **در حکایاتِ هفت‌گانه‌ی شاهنامه** — the seven tales of the Shahnameh

And the café's own system is: **each menu category is given a Shahnameh tale as
its patron, and that tale's image sits faintly behind the text.** Coffee gets
کاوه آهنگر, because the smith's forge and a hot drink are the same fire. The hot
drinks get ضحاک. The cold drinks get خسرو و شیرین, because their love began at a
cold spring.

The name itself is the thesis. **نگاخته** — from نگاشتن, to inscribe; نگاره, an
image. *That which has been inscribed.*

### 1.2 The move

This site has **seven tests**. The Shahnameh has **هفت خان** — the seven trials.
That is not a loose association; it is the same number and the same shape: a
sequence of distinct ordeals, each with its own adversary, undertaken to
recover something.

**The site becomes «هفت خان خودشناسی» — the seven trials of knowing yourself.**

Each test is a خان. Each خان has a patron drawn from the Shahnameh, chosen
because the tale is *about* what the test measures — exactly the logic the café
already uses on its menu. The site is the دفتر in which your passage through
them is inscribed.

This gives us, for free:
- **A reason to take all seven** instead of one. A sequence invites completion.
  Two of the site's existing features — the «انجام شده» badge and the resume
  banner — suddenly mean something.
- **A frame for the result.** Not a score; an inscription.
- **Copy that writes itself,** in a voice the brand already owns.
- **Continuity.** Two properties, visibly one studio.
- **Difference.** Every competitor is a white card with a progress bar.

### 1.3 The patrons

The patron is a **frame, not a replacement.** The psychology is untouched: the
feminine-archetype test still measures the seven Greek goddesses, MBTI still
reports four letters. Renaming the constructs would break the instruments and is
out of scope. The patron sits around the test, in its header, its ornament and
its copy.

| # | خان | Test | Patron | Why this tale |
|---|---|---|---|---|
| ۱ | خانِ نخست | کهن‌الگوهای زنانه | **سیمرغ** | The Simorgh of Alborz: ancient, wise, nurturing, transformative. She raises the abandoned child and gives her feather to heal. The feminine principle in its oldest Persian form. |
| ۲ | خانِ دوم | کهن‌الگوهای مردانه | **رستم** | The archetypal hero — and the traveller of the هفت خان himself. A test asking which hero you are belongs to him. |
| ۳ | خانِ سوم | قطب‌نمای سیاسی | **کاوه آهنگر** | The smith who tied his leather apron to a spear and made it the banner of revolt against Zahhak. The origin of political conscience in Persian myth. Exact fit for a political compass. |
| ۴ | خانِ چهارم | تیپ شخصیتی MBTI | **قلمِ نگارنده** | The brand's own fourth chapter: *the magic pen that writes the name.* MBTI hands you a four-letter name. The pen inscribes it. |
| ۵ | خانِ پنجم | سبک دلبستگی | **خسرو و شیرین** | Persian literature's great study of attachment — longing, avoidance, return, the years of not-quite-reaching. Attachment styles are about how you love. |
| ۶ | خانِ ششم | آزمون رفتاری DISC | **فریدون و فرزندان** | Fereydun divides the world among three sons of three temperaments — the Shahnameh's own meditation on disposition. DISC measures disposition in four dimensions. |
| ۷ | خانِ هفتم | زبان‌های عشق | **بیژن و منیژه** | Manizheh feeds her imprisoned love by begging door to door. Love as *acts*, not declarations — which is the entire premise of love languages. |

**Ordering note.** The خان numbers are a fixed sequence, so the hub stops being
an unordered grid. Tests may still be taken in any order; the number names the
chapter, not a prerequisite.

**On reintroducing numerals.** I removed decorative `۰۱–۰۷` badges from the cards
in the last pass, and I am now putting numerals back. This is a reversal and
worth being explicit about. The badges were floating ornaments on an unordered
list — they numbered nothing. These numerals are the name of the chapter, set
inside the شمسه that *is* the card's identity mark. The number is now content.

---

## 2. Foundations

### 2.1 Colour

#### 2.1.1 Tokens

Inherited wholesale from کافه نگاخته so the two properties read as one studio.
Names are the café's; values are the café's except where measurement forced a
change, which is noted.

```
/* GROUNDS */
--cream:        #F4EBD9   /* the page. See §2.1.3 — measured choice. */
--parchment:    #EDE0C4   /* bands, gates, the darker register */
--paper:        #FBF7EF   /* cards, the text block */
--ink:          #1A1410   /* the dark register: seals, result hero, footer */
--lapis:        #1D3557   /* the night register: sky, the result of a dark خان */
--teal-deep:    #0F4747   /* third dark ground, used sparingly */

/* INKS */
--ink:          #1A1410   /* body text on any light ground */
--ink-soft:     #3D2E22   /* secondary text on light */
--ink-mute:     #6C6255   /* tertiary — cream/paper only, see the law */
--gold-ink:     #7E5D25   /* the only readable gold. cream/paper only. */
--terra-deep:   #8A3217   /* accent text, headings */
--oxblood:      #7A2E1F   /* focus ring, primary accent */
--teal:         #1E6E6E   /* the done-state, cream/paper only */
--lapis:        #1D3557   /* accent text on light */

/* GOLD — FILL AND ILLUMINATION ONLY, NEVER TEXT ON LIGHT */
--gold:         #C9A961   /* rules, ornament, the شمسه, bars */
--gold-bright:  #E6C478   /* highlight within ornament, text on dark */
--gold-shine:   #F5E1A8   /* the innermost highlight only */
--saffron:      #D4912A   /* fill; text on dark grounds only */
--saffron-deep: #A86D18   /* fill and large text only — see the law */
--rose:         #C47A7A   /* fill; text on ink only */
--terra:        #B8451F   /* cream/paper only for text */

/* STRUCTURE */
--rule:         #D9CDB8   /* the hairline. جدول frames, dividers. */
--rule-gold:    #C9A961   /* the illuminated rule */
```

#### 2.1.2 The measured contrast law

Every pair below was computed, not estimated. WCAG AA: **4.5:1** body,
**3.0:1** for large text (≥24px, or ≥18.66px at 700+) and non-text UI.

| ink ↓ / ground → | parchment | cream | paper | ink | lapis | teal-deep |
|---|---|---|---|---|---|---|
| `--ink` | 13.95 | 15.40 | 17.07 | — | 1.48 ✗ | 1.75 ✗ |
| `--ink-soft` | 9.96 | 11.00 | 12.19 | 1.40 ✗ | 1.05 ✗ | 1.25 ✗ |
| `--ink-mute` | 4.57 | 5.04 | 5.59 | 3.05 △ | 2.07 ✗ | 1.75 ✗ |
| `--gold` | 1.72 ✗ | 1.90 ✗ | 2.11 ✗ | **8.10** | **5.49** | **4.64** |
| `--gold-bright` | 1.28 ✗ | 1.41 ✗ | 1.57 ✗ | **10.88** | **7.38** | **6.23** |
| `--gold-ink` | 4.62 | **5.10** | **5.65** | 3.02 △ | 2.05 ✗ | 1.73 ✗ |
| `--saffron` | 2.04 ✗ | 2.25 ✗ | 2.49 ✗ | **6.85** | **4.64** | 3.92 △ |
| `--saffron-deep` | 3.30 △ | 3.64 △ | 4.04 △ | 4.23 △ | 2.86 ✗ | 2.42 ✗ |
| `--lapis` | 9.45 | 10.44 | 11.57 | 1.48 ✗ | — | 1.18 ✗ |
| `--teal` | 4.57 | **5.05** | **5.60** | 3.05 △ | 2.07 ✗ | 1.74 ✗ |
| `--teal-deep` | 7.98 | 8.81 | 9.76 | 1.75 ✗ | 1.18 ✗ | — |
| `--terra` | 4.11 △ | **4.54** | **5.03** | 3.39 △ | 2.30 ✗ | 1.94 ✗ |
| `--terra-deep` | 6.30 | 6.96 | 7.71 | 2.21 ✗ | 1.50 ✗ | 1.27 ✗ |
| `--oxblood` | 7.18 | 7.92 | 8.78 | 1.94 ✗ | 1.32 ✗ | 1.11 ✗ |
| `--rose` | 2.50 ✗ | 2.77 ✗ | 3.06 △ | **5.57** | 3.77 △ | 3.19 △ |
| `--paper` | 1.22 ✗ | 1.11 ✗ | — | **17.07** | **11.57** | **9.76** |

△ = large text and non-text only. ✗ = never.

**The law, in three sentences:**

1. **Light ground → dark ink.** `--ink`, `--ink-soft`, `--oxblood`,
   `--terra-deep`, `--lapis`, `--teal-deep` are safe on any light ground.
2. **Dark ground → gold or paper.** `--gold`, `--gold-bright`, `--saffron`,
   `--paper`, `--cream` are safe on `--ink` and `--lapis`. Nothing dark goes on
   a dark ground.
3. **Gold is a fill.** `--gold`, `--gold-bright`, `--gold-shine`, `--saffron`
   and `--rose` may never carry text on a light ground. When gold must *read* on
   light, it is `--gold-ink`, and only on `--cream` or `--paper`.

#### 2.1.3 Two measurements that changed the design

**`--parchment` is not the page.** The café uses parchment as a ground. Measured
against it, four of our mid-tone inks sit at or under the line: `--gold-ink`
4.62, `--ink-mute` 4.57, `--teal` 4.57, and `--terra` **fails at 4.11**. On
`--cream` all four clear it. So **`--cream` is the page ground and `--parchment`
is demoted to bands and gates** — surfaces that carry headings and ornament, not
body copy. This is measurement overriding inheritance.

**`--saffron-deep` is not a text colour anywhere.** 3.30 / 3.64 / 4.04 on the
light grounds, 4.23 on ink. It fails AA body on every ground the site has. It is
a fill and a large-display colour only. Worth stating because it is exactly the
kind of warm mid-tone that looks readable and is not.

#### 2.1.4 Colour by job, not by decoration

| Job | Colour | Never |
|---|---|---|
| Body text, light ground | `--ink` | any gold |
| Secondary text | `--ink-soft` | `--ink-mute` on parchment |
| Illumination: rules, ornament, شمسه | `--gold` | as text |
| Gold that must be read | `--gold-ink` on cream/paper | on parchment or dark |
| Focus ring | `--oxblood`, inverting to `--gold` on dark | removing it |
| Completed state | `--teal` | green |
| Primary accent / headings | `--terra-deep` | `--terra` on parchment |
| Dark register (seal, hero, footer) | `--ink`, text in `--gold-bright`/`--paper` | dark-on-dark |
| Night register (the ۵th and ۷th خان) | `--lapis`, text in `--gold`/`--paper` | — |

**Dark mode:** out of scope, and deliberately. A manuscript has one ground. The
page declares a single `color-scheme: light` so the browser does not invent one.

### 2.2 Type

#### 2.2.1 The two faces

**Vazirmatn** — Persian and all UI. Already self-hosted as a 38 KB variable
subset (166 codepoints, weights 400–800) with a metric-matched fallback. Stays.

**Cormorant SC** — Latin only, small caps. The café pairs Cormorant with
Vazirmatn; this site inherits the pairing. Its job here is narrow and real: the
Latin acronyms this site is full of — MBTI, DISC, and the D / I / S / C
dimension letters — currently render in Vazirmatn's Latin, which is a
utilitarian sans and looks like a form field in the middle of Persian prose. In
Cormorant SC they read as set type.

Subset to the Latin letters actually used and nothing else. Budget: ≤12 KB.
Scoped by `[lang=en]`, exactly as the café does it, so it can never touch
Persian text.

**Rejected: a Nastaliq display face.** It is the obvious romantic choice and it
is wrong here. Real Nastaliq webfonts run 200 KB+, on an audience with a
constrained network; Nastaliq line-breaking is unreliable in browsers; and it is
illegible below display sizes, so it would buy one headline at the cost of the
whole budget. The manuscript feeling is carried by the **ornament and the
layout** instead — which cost kilobytes, not hundreds of them. This is the
central typographic decision of the plan and it is a deliberate no.

#### 2.2.2 Scale

A single ratio, so nothing is chosen by eye. `clamp()` on display sizes so the
phone is not just a squeezed desktop.

| Token | Size | Weight | Line | Use |
|---|---|---|---|---|
| `--t-display` | `clamp(34px, 6vw, 58px)` | 800 | 1.12 | Landing hero only |
| `--t-h1` | `clamp(28px, 4.4vw, 42px)` | 800 | 1.18 | Screen titles |
| `--t-h2` | `clamp(22px, 3vw, 28px)` | 700 | 1.3 | Section heads, the question |
| `--t-h3` | `19px` | 700 | 1.4 | Card titles |
| `--t-body-lg` | `18px` | 400 | 1.85 | Landing and gate prose |
| `--t-body` | `16px` | 400 | 1.8 | Everything else |
| `--t-sm` | `14px` | 400 | 1.7 | Meta, captions |
| `--t-xs` | `12.5px` | 600 | 1.5 | Labels, the خان numeral |

**Line height is generous on purpose.** Persian has no ascender/descender rhythm
to lean on and its diacritics sit high; 1.8 for body is a floor, not a
preference. Nothing below 1.5 anywhere.

#### 2.2.3 Persian typography law

Non-negotiable, and every one of these has bitten this codebase already:

- **ZWNJ (U+200C)** in every compound that needs it: می‌روی, کهن‌الگو, نیمه‌کاره.
  Never a space, never nothing.
- **Persian keheh ک (U+06A9) and yeh ی (U+06CC)** — never the Arabic ك / ي.
- **Persian digits ۰–۹ (U+06F0–06F9)** in all user-facing numbers, via `toFa()`.
  Never ASCII digits in Persian copy.
- **Persian punctuation:** ٪ not %, ، not comma, ؛ not semicolon, «» not "".
- **`<bdi>` around every run that mixes scripts or digits**, and never a
  bidi-neutral character as a separator between two phrases. A literal `•`
  between «۶۲ گزاره» and «۶ بخش» reorders and renders as «۶۲ گزاره ۶ • بخش` —
  this happened, it shipped, and it was only caught by screenshot. Separators
  are **elements**, not characters.
- **Logical properties only:** `margin-inline-start`, `padding-inline-end`,
  `inset-inline`. No `left`/`right` in any rule that could be mirrored.
- **`direction` styles an element's contents, not its position in its parent.**
  A misunderstanding of exactly this caused the ticker bug on the sibling site.

### 2.3 Space and measure

One 4px base. Only these steps exist: `4 8 12 16 20 24 32 44 64 96`.

| Surface | Measure | Why |
|---|---|---|
| Landing prose | 620px | ~70 Persian characters, the readable maximum |
| Page shell | 900px | the outer container |
| هفت خان index | 900px, 2 columns ≥760px | seven cards, the 7th spans |
| The خان gate | 620px | it is prose |
| **The question** | **560px** | measured: at 860px a Likert row put its radio 740px from its label |
| Result | 700px; the seal 560px | the bars need width, the seal does not |

### 2.4 The illumination system

This is what makes it a manuscript rather than a cream-coloured form. All of it
is **original SVG that I draw** — no licensed art, no stock, no photographs.

**Why drawn, not photographed.** The sibling site's legend artwork is unlicensed
— `rakhsh.webp` carries a visible *fineartamerica* watermark baked into the
pixels, and nothing in the repo credits a source for any of it. It cannot ship
on a public domain. Drawn SVG has no licence risk, is a few KB, scales to any
screen, inherits `currentColor`, prints, and can be themed. Every illustration
slot is built as a swappable component with documented dimensions, so real
commissioned miniatures can drop in later without touching layout.

#### The five motifs

**۱. شمسه — the rosette.** The central Persian manuscript motif: a radiating
medallion. This is the site's primary mark. One drawn SVG, used at four sizes:

| Size | Where | Detail level |
|---|---|---|
| 16–32px | favicon | 8 points, no inner ring — anything more mushes |
| 44px | the خان numeral on each card | 12 points, numeral inset |
| 120px | the gate header, the result seal | 16 points, two rings, inner floret |
| 320px | landing hero, at 8% opacity behind the type | full |

A hard-won lesson applies: the first favicon draft ringed the mark with seven
satellites, one per test. Lovely at 512px, an unreadable smudge at 16. **Detail
is a function of size and the system must say so.**

**۲. سرلوح — the illuminated headpiece.** The band at the head of a manuscript
page. Here: a `--parchment` band, a double gold rule below it (thick/thin, the
manuscript convention), a شمسه centred, the screen title beneath. Opens the
landing, the index, each gate and the result.

**۳. جدول — the ruled frame.** The gold rules that box a manuscript text block.
**This replaces card shadows entirely.** A 1px `--rule` frame with a 3px
`--rule-gold` edge on the inline-start side. Rationale in §2.4.1.

**۴. ترنج — the corner piece.** A quarter-rosette in the corners of the dark
registers (result hero, seal). Gold at 30% on ink. Used at two corners, never
four — four is wallpaper.

**۵. مُهر — the seal.** A drawn oval stamp in `--terra-deep`, slightly rotated,
holding your result's name. The result screen's payoff and the thing worth
screenshotting.

#### 2.4.1 What I am deliberately not copying from the café

The sibling site is the brand and I am matching its world. I am not matching
three of its habits, because they are the generic defaults of 2019 and they
would flatten everything above:

- **Identical rounded cards with soft grey shadows.** The café's café-picker is
  two of them. We use جدول — flat parchment, ruled gold frames. Sharper, more
  like a book, and it costs nothing to render.
- **Tracked-out Latin all-caps eyebrows** (`CHOOSE YOUR CAFÉ`). Our eyebrows are
  Persian with a gold hairline — the pattern this site already has in
  `.ornament`. Cormorant SC appears *inline* for acronyms, never as an eyebrow.
- **Large radii and blurred glows.** Radius scale is `0 / 2px / 50%` and nothing
  else. A manuscript has corners.

This is a judgement call and the client should know I made it. The cream + gold +
terracotta palette is otherwise inherited intact — that combination is on my own
list of tired defaults, and it is exempt here for a specific reason: it is not a
default reached for out of laziness, it is documented brand equity from a
property that already exists. Inheritance, not habit.

---

## 3. Components

Every component ships **six states**: default, hover, focus-visible, selected /
active, disabled, and long-text. Any component that can be empty or loading also
ships those. A component without its states is not done.

### 3.1 خان card (the index)

```
┌ جدول frame, --paper on --cream ────────────────────┐
│ ⟨شمسه 44px، numeral ۱⟩  خانِ نخست                  │  ← --t-xs, --gold-ink
│                                                     │
│ کهن‌الگوهای زنانه                    ⟨badge⟩        │  ← --t-h3
│ پشتیبان: سیمرغ                                      │  ← --t-sm, --terra-deep
│                                                     │
│ کدام الهه‌های اسطوره‌ای در شخصیت تو زنده‌اند؟          │  ← --t-sm, --ink-soft
│ ─────────────────────────────────── gold hairline   │
│ ۷۰ پرسش • حدود ۱۲ دقیقه                   شروع     │
└─────────────────────────────────────────────────────┘
```

| State | Treatment |
|---|---|
| default | `--paper`, 1px `--rule`, 3px `--gold` inline-start edge |
| hover | ground → `#FFF`, the gold edge → 5px, **no transform, no shadow** |
| focus-visible | 3px `--oxblood` ring, offset 2px |
| نیمه‌کاره | badge `--oxblood`; action «ادامه»; edge → `--oxblood` |
| انجام شده | badge `--teal`; action «دیدن نتیجه»; شمسه fills gold |
| long text | title wraps to 2 lines, badge holds `flex-shrink:0`, card grows |

It is a `<button>`. It was a `<div onclick>` and the hub had **zero tab stops** —
nobody on a keyboard could start any test. That is settled and must not regress.

### 3.2 The خان gate (test intro)

سرلوح → the patron's name and two sentences of the tale → what the test measures
and the framework behind it → length, privacy, the caveat → one primary.

The tale is **two sentences, not a paragraph.** Nobody reads a myth before a
quiz. Two sentences earn the frame; five spend it.

### 3.3 Question

Everything from the last pass holds and is not up for redesign — it was measured:

- 560px column; radio adjacent to its label
- `role=radiogroup`, roving tabindex, arrows move and select, Home/End
- digits ۱–۵ / 1–5 answer; auto-advance 260ms, switchable, remembered, never
  from an arrow key, never on the last question
- 6px progress track on `--rule` (3px on `--bg-deep` measured **1.08:1** — an
  invisible bar); counts answers, not position
- `role=progressbar` with `aria-valuetext`
- focus moves to the question heading on change, never on re-render

**What changes is only the dress:** the قلمِ نگارنده hairline above the question,
the option rows as جدول, the selected row inverting to `--ink` with a gold
marker, the progress rule rendered as an illuminated rule.

### 3.4 Result seal

```
        ⟨سرلوح⟩
   ┌ --ink, ترنج corners ─────────┐
   │        ⟨شمسه 120px⟩          │
   │      کهن‌الگوی غالب تو        │  --gold-bright, --t-xs
   │          آرتمیس              │  --paper, --t-h1
   │   ⟨two-line description⟩     │  --cream, --t-body
   │      ⟨مُهر، rotated⟩          │
   └──────────────────────────────┘
   ranked bars, every row with a folded توضیح
   ⟨share primary⟩ ⟨restart⟩ ⟨index⟩ ⟨print⟩
```

Tie handling is settled and must survive: a flat result names no winner, shared
first places are all named in a Persian list, a runner-up within 3 points is
mentioned. The seal must render all four cases — including «الگوی غالبی پیدا
نشد», which is a sealed result too, not an error.

### 3.5 Buttons

| Variant | Treatment |
|---|---|
| primary | `--ink` ground, `--cream` text, 4px `--gold` offset block shadow |
| ghost | transparent, 1px `--rule`, `--ink-soft` text |
| quiet | text only, underlined, `--ink-mute` — for انصراف and similar |
| disabled | transparent, **1px dashed** `--rule`, `--ink-mute` |

Disabled being *flat and dashed* is deliberate: a filled block with a drop
shadow reads as "press me" whatever its colour, and the disabled Next button was
measurably louder than the enabled ghost beside it.

No arrow glyphs in button labels. Vazirmatn has no ← → ↔ ✓ glyph, so every one
rendered from whatever fallback the device had, at a different weight and
baseline. They are gone and they stay gone.

---

## 4. Structure

### 4.1 Route map

One file, hash router — the existing router, extended. Two new routes.

| Route | Screen | Title |
|---|---|---|
| `#/` | **دیباچه — landing** (new) | نگاخته — هفت خان خودشناسی |
| `#/khan` | هفت خان index | هفت خان خودشناسی — نگاخته |
| `#/t/<id>` | the خان gate | ⟨test⟩ — نگاخته |
| `#/t/<id>/q/<n>` | question | پرسش ۱۲ از ۷۰ — ⟨test⟩ |
| `#/t/<id>/r` | result | نتیجهٔ ⟨test⟩ — نگاخته |
| `#/daftar` | **دفتر — about** (new) | دفتر نگاخته |

The hub moves from `#/` to `#/khan` and `#/` becomes the front door. `#/` must
therefore keep rendering something useful for anyone with the old URL — it does,
it is the landing, and the landing's primary goes straight to `#/khan`.

### 4.2 Landing — دیباچه

The thing the site has never had. Above the fold on a phone:

1. سرلوح with the شمسه
2. `--t-display`: **خودت را بهتر بشناس** — kept; it tests well and it is direct
3. One line: هفت آزمون، هفت خان. بر پایهٔ چارچوب‌های شناخته‌شدهٔ روان‌شناسی.
4. Primary → `#/khan`. Secondary → `#/daftar`.
5. Three facts as a ruled row, not cards: **بدون ثبت‌نام · نتیجهٔ فوری · پاسخ‌ها فقط در مرورگر تو**

Then: the seven خان as a numbered sequence (not the full cards — names and
patrons only, a table of contents); how it works in three steps; the caveat.

**The privacy line is a selling point, not fine print.** "Your answers stay in
your browser" is genuinely rare and this audience cares. It goes above the fold.

### 4.3 دفتر — about

The manuscript voice, in the register the café already established: a short
دیباچه, then what نگاخته means, the هفت خان and each patron, how results are
computed and what they are *not* (§4.4), and the privacy model in plain words.

### 4.4 The honesty section

These tests are entertainment built on real frameworks, and the site currently
says so once, quietly, in the footer. It gets a proper section, because being
straight about it is a mark of quality, not a disclaimer:

- what each instrument is and is not
- that the Likert scale bottoms out at 20%, not 0 — see §7 open items
- that a flat answer sheet cannot produce a result, and why
- that nothing is sent anywhere

---

## 5. Motion

Restrained. A manuscript does not animate.

| Element | Motion | Duration |
|---|---|---|
| Screen change | opacity only, no translate | 180ms |
| Gold rule on a سرلوح | draws in from the inline-start | 420ms, once |
| Bar fill on the result | width, staggered 60ms | 700ms |
| Card hover | ground and edge width | 180ms |
| Focus ring | none — appears instantly | 0 |

**Banned:** fade-and-slide-up reveals, parallax, any transform on hover, any
scroll-triggered animation, the ring transitioning in (it made the ring measure
0px mid-transition and cost half an hour of false debugging).

`prefers-reduced-motion: reduce` zeroes every duration. Currently measured at
**30 animated elements → 0**; that must stay 0.

---

## 6. Non-negotiables

### 6.1 Accessibility

- Every interactive thing is a real `<button>`, `<a>` or input. No `div onclick`.
- Visible `:focus-visible` on everything focusable — 3px `--oxblood`, inverting
  to `--gold` on dark grounds.
- AA on every text node against **its real painted ground**, verified by sweeping
  the rendered DOM, not by reading the stylesheet.
- Target ≥44×44px for anything tapped.
- Semantic headings in order; one `<h1>` per screen.
- `aria-live` for the question counter; `role=progressbar` with `aria-valuetext`.
- Reduced motion honoured.
- Keyboard: the whole site completable without a mouse, including all seven tests.

### 6.2 Performance budget

| | Budget | Now |
|---|---|---|
| HTML+CSS+JS (one file, gzipped) | ≤ 60 KB | ~34 KB |
| Vazirmatn subset | ≤ 40 KB | 37.9 KB |
| Cormorant SC subset | ≤ 12 KB | — |
| Ornament SVG (inline, total) | ≤ 8 KB | — |
| OG cards (crawler-only) | ≤ 25 KB each | 17.5 KB |
| **Total first paint** | **≤ 120 KB** | ~72 KB |
| Third-party requests | **0** | 0 |

Zero third-party requests is a hard rule. This audience is on networks where
Google Fonts does not resolve.

### 6.3 Validation gates — a phase is not done until these pass

Existing scripts, all of which must stay green:

| Script | Checks |
|---|---|
| `contrast.py` | every visible text node vs its real ground, 2 widths × 11 screens |
| `verify22.py` | digits, auto-advance, arrow isolation, last-question guard |
| `verify23.py` | ties: flat, 2-way, 3-way, near-miss, MBTI axes, compass centre |
| `verify24.py` | tab stops, state-aware actions, bidi separator, overflow 320→1920 |
| `regress.py` | deep links, Back, resume, radiogroup |
| `tools/build_font.py --check` | every displayable codepoint has a glyph |

New for this project:

| Script | Checks |
|---|---|
| `check_ornament.py` | every شمسه size renders, no clipped viewBox, favicon legible at 16px |
| `check_weight.py` | the §6.2 budget, per surface, fails the build when over |
| `check_bidi.py` | no bidi-neutral character used as a separator anywhere |

And the rule that catches what scripts cannot: **screenshot at 375 / 768 / 1440,
look at the images, write down what is wrong, fix it, screenshot again.** Every
serious defect in this codebase so far was found by looking, not by testing — the
stranded icon, the blurred band, the invisible progress bar, the reordered
bullet, the hub with no keyboard.

---

## 7. Implementation phases

Each phase is committable, shippable, and independently verifiable.

| # | Phase | Deliverable | Gate |
|---|---|---|---|
| **1** | Foundations | tokens rewritten on §2.1; `color-scheme`; space and type scales; Cormorant SC subset + build tool | contrast, font-check, weight |
| **2** | Illumination | the five motifs as drawn SVG; شمسه at 4 detail levels; favicon and icon set redrawn | `check_ornament.py`, 16px legibility |
| **3** | Landing (دیباچه) | new `#/` screen; hub moves to `#/khan`; router, titles, canonical | regress, contrast, 3 widths |
| **4** | هفت خان index | cards on جدول; شمسه numerals; patrons; the 7th spanning | verify24, contrast, 3 widths |
| **5** | The خان gate | سرلوح, patron, tale, framework, caveat | regress, contrast |
| **6** | Question dress | ornament only — **zero mechanical change** | verify22, regress, contrast |
| **7** | Result seal | dark register, ترنج, مُهر, bars, all four tie cases | verify23, contrast, 3 widths |
| **8** | دفتر (about) | new `#/daftar`; manuscript voice; the honesty section | contrast, 3 widths |
| **9** | Share layer | per-test OG cards; static entry stubs so a linked test previews as itself | weight, manual preview check |
| **10** | Final pass | full suite; 375/768/1440 critique; weight; `DESIGN.md` reconciled to shipped code | everything |

**Phase 6 carries the project's main risk.** The question screen's mechanics took
three rounds and four bug fixes to get right. It gets a new dress and nothing
else. `verify22.py` and `regress.py` run before and after, and any diff in
behaviour is a defect, not a trade-off.

**Phase 9 removes a limitation I previously reported as unfixable.** Per-test
share previews are impossible with hash routing because a fragment is never sent
to a server. Seven small static entry files — each with its own `og:` tags,
redirecting into the app — fixes it without a server. It is listed last because
it is additive and independent.

---

## 8. Decision log

| Decision | Alternative | Why |
|---|---|---|
| هفت خان frame | generic modern editorial | the brand already owns this world; nothing else in the category looks like it |
| Original SVG ornament | reuse the sibling's legend art | that art is unlicensed and one file is visibly watermarked |
| `--cream` as page ground | `--parchment`, as the café uses | measured: `--terra` fails at 4.11 on parchment |
| Vazirmatn 800 for display | a Nastaliq face | 200 KB+, unreliable line-breaking, illegible at body size |
| جدول frames | rounded cards with soft shadows | the café's habit and the category's default; flat rules read as a book |
| No dark mode | a full second theme | a manuscript has one ground; and it doubles the contrast matrix |
| Numerals return to the cards | leave them off | they now name a chapter in a sequence; before they numbered nothing |
| Cormorant SC for Latin only | Vazirmatn's Latin | MBTI/DISC set in a UI sans looks like a form field mid-sentence |

## 9. Open items for the client

1. **Domain and folder.** Not yet known. Nothing in the build hardcodes one —
   canonical and `og:url` are computed from wherever the page sits — so this
   blocks nothing, but Phase 9's static stubs want to know the path.
2. **Deployment.** There is no pipeline in this repo; the site is uploaded by
   hand. Worth deciding whether that stays true before Phase 9 adds files.
3. **The Likert floor.** Agreeing with nothing in a category still shows a 20%
   bar, because the scale runs 1–5 rather than 0–4. Rescaling changes every
   stored result. My recommendation: leave the maths, label the axis honestly in
   §4.4. Needs a decision.
4. **Commissioned artwork.** Every illustration slot is swappable. If there is a
   budget for real miniatures, the frame is ready for them.
5. **The seventh patron.** بیژن و منیژه is my choice for love languages. If the
   brand has a preferred tale, it is a one-line change.
