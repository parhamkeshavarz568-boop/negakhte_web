#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Record today's prices into the price history.

    python3 build/snapshot_prices.py              # record today
    python3 build/snapshot_prices.py --date 2026-09-01

Run this EVERY TIME you change prices in build/data/products.source.json, then
rebuild. That is what makes the price index work — the site can only show a
trend for movement it has actually observed.

Storage is one row per SKU, appended only when the price CHANGES:

    {"AMO-001": [["2026-09-14", 25987500], ["2026-09-21", 26500000]], ...}

Storing changes rather than a daily row keeps the file small and makes "last
changed" exact. A price that holds for three weeks is one entry, not 21.

Dates are Gregorian ISO-8601 because that is what machines need; the site
renders them as Jalali for readers.

IMPORTANT: this file is the only source of price history. Nothing is inferred
or back-filled — a chart is never drawn from a single observation, because a
trend line through one point would be an invention, and these are prices
customers act on.
"""
import json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "data", "products.source.json")
HIST = os.path.join(HERE, "data", "price-history.json")


def load_history():
    if os.path.exists(HIST):
        return json.load(open(HIST, encoding="utf-8"))
    return {}


def main():
    date = None
    if "--date" in sys.argv:
        date = sys.argv[sys.argv.index("--date") + 1]
        datetime.date.fromisoformat(date)          # validate
    date = date or os.environ.get("SNAPSHOT_DATE") or datetime.date.today().isoformat()

    products = json.load(open(SRC, encoding="utf-8"))
    hist = load_history()

    added = unchanged = skipped = 0
    for p in products:
        sku, price = p["s"], p["p"]
        if not isinstance(price, int):
            skipped += 1                            # unpriced: nothing to record
            continue
        series = hist.setdefault(sku, [])
        if series and series[-1][1] == price:
            unchanged += 1
            continue
        if series and series[-1][0] == date:
            series[-1] = [date, price]              # same-day correction
            added += 1
            continue
        series.append([date, price])
        added += 1

    for sku in hist:
        hist[sku].sort(key=lambda r: r[0])

    json.dump(hist, open(HIST, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    pts = sum(len(v) for v in hist.values())
    with_trend = sum(1 for v in hist.values() if len(v) >= 2)
    print(f"snapshot {date}")
    print(f"  recorded a new price for   {added} SKU(s)")
    print(f"  price unchanged for        {unchanged} SKU(s)")
    print(f"  no price to record         {skipped} SKU(s)")
    print(f"  history now holds          {pts} observations across {len(hist)} SKUs")
    print(f"  SKUs with a real trend     {with_trend}"
          + ("   (need >=2 observations before any chart is drawn)"
             if with_trend == 0 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
