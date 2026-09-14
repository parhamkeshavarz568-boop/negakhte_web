# Measured numbers

Nothing in here is an estimate. Every figure comes from running the built site
in headless Chromium at DPR 2, or from the files on disk. Reproduce with:

```bash
python3 -m http.server 8901 --directory public &
PORT=8901 python3 build/measure_weight.py
```

## Rendered box sizes — why the images are the sizes they are

| element | mobile 390 | tablet 768 | desktop 1440 | renditions shipped |
|---|---|---|---|---|
| hero | 390×541 | 768×589 | 1440×597 | 640, 1024, 1500 |
| category thumbnail | 160×160 | 160×160 | 160×160 | 160, 320, 400 |
| product card image | 187 | 245 | 283 | 400, 600 |
| product detail photo | 318 | 380 | 380 | 400, 600, 700 |

The category thumbnails originally rendered at 108 px while being *shipped* at
400 px — a 3.4× pixel-count overspend. The redesign made them image-forward at
160 px, so they now ship at 160/320 and the same files are reused at 400 for
product cards (the sources are 400×400, so that is the largest honest size).

## First-load transfer weight

Over-the-wire, gzip applied to text, AVIF chosen by the browser:

| page | mobile | desktop |
|---|---|---|
| home (15-product slider) | **119.8 KB** | 139.5 KB |
| category (50 products) | 93.6 KB | 93.6 KB |
| product | 90.1 KB | 116.2 KB |
| brand | 90.8 KB | 90.8 KB |

The visual redesign *reduced* the home page (107.3 → 103.7 KB on mobile): the
extra 2.9 KB of gzipped CSS was more than paid for by right-sizing the
category imagery.

Repeat visits are HTML only — around 6–10 KB — because the font, CSS and JS
are cached for a month or a year.

For comparison, the original single-page draft was **474 KB of HTML** (324 KB
gzipped) on *every* view, since the images were base64-inlined and therefore
uncacheable, plus 255 KB of font across 5 requests to jsDelivr.

`build/measure_weight.py` fails if any page exceeds **150 KB**.

## What dominates, and why it stays

The font is the single largest asset on every page at **57.1 KB**. That is one
variable WOFF2 covering weights 100–900 for the whole Persian alphabet plus
ASCII. The alternatives were worse:

- upstream's nine static faces: 255 KB across 5 requests
- static 400+700 only: smaller, but the design uses 450/500/550/600 and those
  would silently snap to the nearest available weight
- the full Arabic block rather than an explicit Persian codepoint list: 68.3 KB

It is cached for a year, so it is paid once per visitor.

## Image format savings

AVIF is **64% smaller than JPEG** across the whole set. WebP is kept as the
middle layer — not redundant, it is what serves the older Android WebView tail
still common in Iran, which AVIF misses.

The hero carries a lower quality (AVIF q38) than the product photos (q54)
because it sits under a `rgba(0,0,0,.82)` → `rgba(0,0,0,.15)` gradient scrim.
At that opacity the detail is not visible: 30.4 KB instead of 57.3 KB at
1500 px for a difference nobody can see.

## Layout checks that passed

At 390, 768 and 1440 px: no horizontal overflow on any page, one `<h1>` per
page, no heading-level jumps, and every image box has intrinsic
width/height so nothing reflows as images arrive.

## Contrast

All **21** text/background pairs in the palette clear WCAG AA (4.5:1),
re-verified after the visual redesign changed most of them. Lowest passing
pair is `--muted` on the page ground at 4.81:1.

The brand yellow `#fbb316` is 1.9:1 on white and is never used as text — a
darkened `--gold-ink` (#8a5600, 6.16:1 on white) carries link and accent text
instead.

Neutrals are warm-tinted rather than pure grey: a neutral grey next to an
amber accent reads cold, so the page ground is `#f4f2ef` and the shadows are
tinted `rgba(28,22,8,…)` rather than black.


## Core Web Vitals

Measured from the real `PerformanceObserver` entries in headless Chromium,
across 7 pages × 3 viewports (`PORT=8907 python3 build/check_layout.py`):

| metric | result | Google's "good" bar |
|---|---|---|
| **CLS** | **0.000 on all 21 combinations** | < 0.1 |
| **LCP** | 48–176 ms | < 2500 ms |
| Long tasks | 0 on most pages, 1 on the 77-card category page | — |

LCP is measured off localhost, so it excludes network time — what it proves is
that there is no render-blocking work: one stylesheet, a deferred script, and
a preloaded font.

CLS of exactly zero comes from every image carrying intrinsic
`width`/`height`, `aspect-ratio` on each image box, metric-matched fallback
faces so the font swap does not reflow text, and the slider controls shipping
`hidden` inside a reserved-height row rather than appearing and pushing
content down.

## `content-visibility`: tried, measured, removed

`content-visibility: auto` with `contain-intrinsic-size: auto 420px` on the
features and FAQ sections was measured producing **up to 765px of phantom
scroll height** — the desktop category page reported 12840px on load and
collapsed to 12075px once scrolled, so a user could scroll into space that
stopped existing.

The estimate is tunable per breakpoint, but it silently re-breaks whenever the
content changes, and these are static pages where skipping the render of a
four-item feature row buys close to nothing. Layout and paint containment on
the cards gives the scroll-performance benefit with none of the sizing risk.

`build/check_layout.py` now fails on any scroll-height drift over 2px, so this
cannot be reintroduced unnoticed.

## What makes navigation feel instant

- **Speculation Rules** (`/speculation-rules.json`, referenced by a
  `Speculation-Rules` HTTP header) prerender a same-origin page after ~200ms
  of link hover, so the click lands on an already-painted page. Delivered as
  an external file rather than an inline `<script type="speculationrules">`
  so the CSP stays at a strict `script-src 'self'`.
- **Cross-document view transitions** (`@view-transition { navigation: auto }`)
  cross-fade between pages instead of flashing white. The masthead, menu bar
  and footer are named, so they stay planted while the content changes.
- **Scroll-driven reveals** (`animation-timeline: view()`) animate cards in as
  they enter the viewport with no scroll listener and no main-thread work —
  it runs on the compositor. Wrapped in `@supports` and disabled under
  `prefers-reduced-motion`.
