============================================================
  Negakhteh Cafe — Source Files
============================================================

This folder contains the SOURCE versions of your HTML files —
fully commented and unminified, so you can read and edit them.

------------------------------------------------------------
  WORKFLOW
------------------------------------------------------------

  1. Edit source/index.html or source/about.html
  2. Re-minify (ask Claude, or run a minifier yourself)
  3. The minified versions go in the parent folder
  4. Upload the parent folder to your web host

The minified versions (in the parent folder) are what gets
served to visitors — they're 42% smaller than the source.

------------------------------------------------------------
  WHAT TO UPLOAD TO YOUR WEB HOST
------------------------------------------------------------

Upload everything EXCEPT this `source/` folder. So:

    index.html       <- minified production version
    about.html       <- minified production version
    .htaccess        <- server config (cache headers, gzip)
    images/          <- all images and self-hosted fonts

DO NOT upload `source/` — that's just your editing copy.

------------------------------------------------------------
  WHY FONTS ARE SELF-HOSTED
------------------------------------------------------------

The site no longer loads fonts from Google. Google Fonts is
unreliable in Iran — many users were getting blank screens
or refresh loops because the page wouldn't render until the
font CSS arrived (which sometimes never did).

All fonts now live in `images/fonts/` and are served from
your own server. The site is fully self-contained and has
no external dependencies.

------------------------------------------------------------
  KNOWN MISSING FILE
------------------------------------------------------------

The CSS references `images/legends/rostam.webp` for the
Hot Drinks category, but the file doesn't exist. Hot Drinks
currently has no legend background painting.

To fix: either provide a Rostam-alone painting as
`images/legends/rostam.webp`, OR change the line in
source/index.html from `url('images/legends/rostam.webp')`
to point at one of the existing files.

------------------------------------------------------------
  KNOWN BACKDROP-FILTER MINIFIER QUIRK
------------------------------------------------------------

The minify-html tool incorrectly drops the unprefixed
`backdrop-filter` property when both prefixed (-webkit-)
and unprefixed are present in source. This breaks the
frosted-glass effect on menu cards in Chrome/Firefox.

The build pipeline (handled by Claude) automatically
re-adds the unprefixed property after minification. If
you minify with a different tool, watch for this.

------------------------------------------------------------
  ⚠  IMPORTANT — SOURCE IS OUT OF DATE (read before editing)
------------------------------------------------------------

The workflow described above is currently BROKEN.

`source/index.html` has fallen behind the live `index.html`.
The live file contains at least one feature the source does
not: the café chooser overlay (`#cafeChooser`, the "which
café are you visiting?" screen). It also already had several
performance fixes that were never written back to source.

So: DO NOT re-minify `source/index.html` over the live
`index.html`. Doing that would silently delete the café
chooser and re-introduce old performance bugs.

The performance work described below was applied DIRECTLY to
the minified `index.html`, for that reason.

Before using the source workflow again, someone needs to
bring `source/index.html` back in sync with the live file.

------------------------------------------------------------
  PERFORMANCE FIXES APPLIED (to index.html directly)
------------------------------------------------------------

All features were kept. Only HOW they are drawn changed.

1. body::before — the ambient background drift animated
   `background-position`, which is not a compositable
   property. It repainted the ENTIRE viewport 60x/second,
   forever. Now animates `transform` on a slightly oversized
   layer instead. Same drift, zero repaint.

2. .ambient-wash — had `transition: background .4s` while JS
   rewrote its background every frame, so every frame started
   a fresh 400ms gradient interpolation on a full-screen
   `multiply`-blended layer. Transition removed (the JS
   already interpolates continuously, so no visual change).

3. .celestial .sun-bloom — had the exact same
   `transition: background .4s` bug, on a blurred,
   screen-blended element sitting on the sun. Removed.

4. .parallax-layer-1 — had `filter: blur(2px)` applied to a
   FULL-VIEWPORT tiled pattern, at 6% opacity. This was the
   single most expensive thing on the page. The blur is
   static, so it is now baked into the SVG tile itself via
   <feGaussianBlur>. Identical look, rasterized once.

5. .tile-band — animated `background-position` across two
   full-width strips. Now a transform marquee on a ::before
   (640px = 10 tiles, so it still loops seamlessly).

6. Sky repaint throttle — the existing throttle was measured
   in VIRTUAL hours (0.05h). But the intro time-lapse
   compresses 16 virtual hours into 8 seconds, so that gate
   still allowed ~40 full-viewport gradient repaints per
   second during exactly the moment the user is watching the
   sun move. Added a wall-clock throttle (100ms) on top, with
   a `force` flag so the final settle still paints correctly.

7. Menu item 3D tilt — called getBoundingClientRect() on
   every single mousemove (forced synchronous layout). Now
   caches the rect on mouseenter and rAF-throttles the write.

------------------------------------------------------------
  ROUND 2 — TWO BUGS THAT WERE NOT PERFORMANCE PROBLEMS
------------------------------------------------------------

8. THE SUN/MOON TIME-LAPSE WAS PLAYING BEHIND THE CHOOSER.
   The intro sweep was fired by `setTimeout(startIntroOnce, 1500)`
   on page load. But the café chooser is an OPAQUE full-screen
   overlay (z-index 400) that stays up until the user picks a
   café. So the entire 8-second sun/moon arc ran, finished, and
   settled while nobody could see any of it. By the time the menu
   appeared, the sun was already parked at the current hour and
   only moved on scroll — which reads as "the movement is stuck".
   Measured: 22 sun position changes while the chooser was up,
   then none afterwards.
   FIX: the sweep now starts when a café is selected (waiting for
   the splash if it's still up). Measured after: 1 position change
   while the chooser is up, 55 once the menu appears.

   Also: the sweep used to abort on ANY scroll event, including a
   1px or programmatic one. It now aborts only on a real scroll
   of more than 40px.

9. THE PAGE SCROLLED PAST ITS OWN CONTENT INTO EMPTY SPACE.
   Two causes stacked:

   a) `.category` had `content-visibility: auto` with
      `contain-intrinsic-size: auto 800px`, and `.footer` had a
      600px equivalent. Un-rendered categories reported a fake
      800px each. Document height was 4518px on arrival and
      collapsed to 3902px as you scrolled — a 616px phantom. You
      could scroll into space that stopped existing once you got
      there. Removed; heights are now real and stable from load.

   b) The zodiac stars are position:absolute on <body>, placed at
      up to 0.95 of document height — and they were positioned
      while the fake 800px placeholders were still inflating that
      height. One ended up at 4740px, 222px BELOW the footer,
      holding the scrollable area open over nothing. They are now
      clamped above the footer and repositioned again after
      layout settles.

   Measured after: scrollHeight 3902 at load, still 3902 at the
   bottom, 0px gap, lowest element on the page is the footer.

   Removing content-visibility also made it FASTER, not slower —
   the constant render/unrender of categories during scroll cost
   more than it saved at this page size.

------------------------------------------------------------
  ROUND 3 — "FAST AT THE START, THEN THE MOON STICKS"
------------------------------------------------------------

10. THE SCROLL RANGE WAS CACHED BEFORE THE MENU EXISTED.

    The scroll-driven celestial divides scrollY by a cached
    `_cachedScrollable` value. That cache is computed at script
    parse time and refreshed on `load` — but at BOTH those moments
    `<main>` is still completely empty, because the menu HTML is
    injected later by the café-chooser script. It was also only
    ever refreshed again on a viewport WIDTH change.

    So the cache held roughly 600px while the real scrollable
    range is about 3000px. `scrollY / 600` saturates at 1.0 after
    600px of scrolling, which means the sun and moon raced through
    their entire 12-hour offset inside the first fifth of the page
    and then sat completely still for the remaining 80%.

    Measured before (moon-x against scroll):
        300px -> 70.1vw
        600px -> 87.7vw
        901px -> 87.7vw   <- frozen
       3002px -> 87.9vw   <- still frozen

    Measured after:
        300px -> -4.7vw     1501px -> 36.4vw
        600px ->  5.6vw     2101px -> 57.1vw
        901px -> 15.9vw     2702px -> 77.7vw
       1201px -> 26.1vw     3002px -> 87.9vw
    — an even ~10vw per 10% of page, all the way down.

    FIX: the cache is recomputed once the menu has been injected
    (and again 1.2s later once layout settles). It is also now
    self-healing: if scrollY is ever greater than the cached
    maximum, the cache is stale by definition and gets refreshed.
    The original iOS URL-bar protection (ignore height-only
    resizes) is untouched.
