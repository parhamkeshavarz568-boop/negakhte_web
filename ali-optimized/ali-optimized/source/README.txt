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
