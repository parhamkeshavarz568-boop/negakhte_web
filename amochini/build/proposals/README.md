# Proposals — NOT wired into the build

Nothing in this directory runs. `build/all.sh` does not call it, `build.py`
does not read it, and `public/` is byte-identical whether it exists or not.
It holds design work that has been built and looked at but not chosen.

## chinese-ornament — a fret rule and a seal for the board band

Two pieces, both drawn as SVG, both in `--amber`, both decorative
(`aria-hidden`), proposed for `.bb-photo` (DESIGN.md §14.4):

**The fret** — a 雷纹 "cloud-and-thunder" band, the rectilinear key motif off
Chinese bronzes, as a 14px hairline rule along the TOP edge of the
photograph, where it frames the picture the way a mounted scroll's border
does. 44px pitch, 1.6px stroke, 85% opacity, and masked to fade out over the
outer 13% at each end so it reads as an ornament rather than as a border of
the browser window. Four weights and two pitches were built and looked at on
the real page at 390 and 1440 first: at 1.2px it disappears against the
photograph on desktop, and edge-to-edge (no fade) reads as a rule someone
drew across the viewport.

**The seal** — a 刹车 ("brake") chop, 44px, in the band's end corner, which
in RTL is the left: where a seal goes on a Chinese painting. `make_seal.py`
builds it from the WenQuanYi Zen Hei outlines into **pure SVG paths**, so no
CJK webfont ships — the whole mark is 1.5 KB of path data with no font
dependency and no network request. Re-run it only if the characters change.

    python3 build/proposals/make_seal.py       # writes seal-shache.svg

The glyphs are centred on their INK box, not the em box; a CJK em box is
taller than its ink and the seal sits visibly high if you trust it.

**Why these two and not clouds.** 祥云 cloud scrollwork was drawn twice. The
first attempt read as generic cartoon clouds; the second, with proper 如意
spiral heads, was genuinely handsome but vanished at any opacity low enough
not to compete with the photograph. Both are in the session history, neither
is here. Restraint is what makes this read as craft rather than as stickers.

**Nothing claims anything.** 刹车 is descriptive — it says "brake", the thing
the shop sells. A seal reading 正品 ("genuine article") was considered and
dropped: it would read as a certification mark that no one issued, which is
the same mistake as the empty trust badges that were removed from the footer.

## To adopt it

The pieces go inside `.bb-photo` in `pages.py:home()`, with the CSS in
`site.css` beside the `.bb-photo` rules. Then, before it can ship:

- re-run `build/check_contrast.py` — the seal sits over the photograph
- re-run `build/measure_weight.py` — both marks are inline SVG, so they land
  in the HTML of `/` and count against the 150 KB budget (~1.8 KB together)
- add a §14 named exception to DESIGN.md, per the rule that no new value gets
  used before it is written down
