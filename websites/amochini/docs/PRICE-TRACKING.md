# Price tracking

The site's differentiator: every product's price is recorded each time it
changes, so the page can show *when* it moved and *by how much*. That is a
price index, not a catalogue — and «قیمت روز» is a query Iranians actually
search.

## The one rule

**Nothing is ever inferred, smoothed or back-filled.** A product with one
observation has no trend, so it gets no percentage and no chart — it shows its
price and the date that price was recorded. A line through a single point would
be an invented price movement, and these are numbers customers act on.

Charts and deltas appear automatically, per product, from its **second**
recorded price onward.

## The loop you need to run

Every time you change prices:

```bash
# 1. edit the prices
#    build/data/products.source.json  ->  "p" is the price in RIAL

# 2. record the change
python3 build/snapshot_prices.py

# 3. rebuild
python3 build/build_catalog.py && python3 build/build.py && python3 build/validate.py
```

Step 2 is the one that matters. **Skip it and the site has no history to show** —
it will keep displaying the last recorded price as though nothing moved.

`snapshot_prices.py` appends a row only when a price actually differs, so a
price that holds for three weeks is one entry, not twenty-one. That is what
makes "last changed" exact.

Backdating is supported if you have older prices on paper:

```bash
python3 build/snapshot_prices.py --date 2026-08-01
```

## Where it shows up

| Surface | What appears |
|---|---|
| `/prices/` | the full board — every priced SKU, its price, delta, sparkline and date; filterable by part, car and direction |
| home page | top movers table + a link to the board |
| product card | delta chip + sparkline under the price |
| product page | the delta, a history chart with min/max, and a collapsible table of every recorded price |

## Design decisions worth knowing

**Up is red, down is blue — and up means *bad*.** For someone buying a brake
disc a price rise is bad news, so it wears the warning tone. That is the
inverse of a stock ticker and it is the right way round here.

**Not red/green.** Red↔green is the most common colour-vision collision and
the pair measured ΔE 5.6 under deuteranopia — below even the floor that
secondary encoding can rescue. Red↔blue measures ΔE 22.5 and passes every
check. Every chip also carries an arrow and a word, so colour is never
carrying the meaning alone.

**A sub-0.1% move says «کمتر از ۰٫۱٪», not «۰٪».** A "0% decrease" reads as no
change at all.

**Time runs left-to-right in the charts** even though the page is RTL. A chart
is a picture rather than text, and every financial chart the audience has seen
runs that way — mirroring it would make a rising line read as falling. If you
disagree, it is one change in `prices.py`.

**Prices are stored in Rial and displayed in Toman.** The charts, the tables
and the structured data all derive from the one stored integer, so they cannot
drift apart. `validate.py` asserts it on every build.

## Previewing the design before you have history

With a single snapshot the whole feature is correctly invisible. To see what it
becomes:

```bash
python3 build/make_preview.py     # -> /tmp/amochini-preview
```

That builds a throwaway copy with synthetic movement and a loud red banner on
every page saying the data is fake. It never touches `public/` or the real
history file. Use it to review the design, never to show a customer.
