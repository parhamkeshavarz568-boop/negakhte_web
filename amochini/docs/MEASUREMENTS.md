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
| category thumbnail | 108×108 | 108×108 | 108×108 | 108, 216 |
| product card image | 187 | 245 | 283 | 400, 600 |
| product detail photo | 318 | 380 | 380 | 400, 600, 700 |

The category thumbnails render at **108 px at every viewport**. They were
originally being shipped at 400 px — a 3.4× pixel-count overspend on every
home-page load, for a box that never gets bigger.

## First-load transfer weight

Over-the-wire, gzip applied to text, AVIF chosen by the browser:

| page | mobile | desktop |
|---|---|---|
| home | **107.3 KB** | 141.4 KB |
| category (50 products) | 79.6 KB | 79.6 KB |
| product | 75.7 KB | 105.7 KB |
| brand | 77.0 KB | 77.0 KB |

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

Every text/background pair clears WCAG AA (4.5:1). Three failed before and
were corrected — see `git log`:

| token | before | after |
|---|---|---|
| `--muted` on the page ground | 4.06:1 | 4.55:1 |
| card SKU text | 2.85:1 | 5.10:1 |
| gold link colour | 4.05:1 | 5.21:1 |

The brand yellow `#fbb316` is 1.9:1 on white and is never used as text — a
darkened `--gold-ink` (#996000, 5.21:1) is used instead.
