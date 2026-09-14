#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed build/data/price-history.json with a fabricated upward price series for
every priced SKU.

    python3 build/seed_prices.py            # write the series
    python3 build/seed_prices.py --weeks 16 # a longer history
    python3 build/seed_prices.py --check    # report what is on disk

WHAT THIS IS, PLAINLY
---------------------
The numbers this writes are INVENTED. The owner asked for a populated board
now rather than in three months, and confirmed it after being told what the
trade-off is. Two guardrails are therefore built in and must stay:

  1. The LAST observation of every series is the product's REAL catalogue
     price, to the rial. So the figure a customer sees, phones about and pays
     is the true one; only the path behind it is modelled. validate.py asserts
     this against the schema.org Offer on all 116 priced pages.

  2. None of the invented series reaches structured data. schema.org carries
     the current Offer price only — which is real — and the JSON/CSV feeds are
     generated from the same file, so they carry a `synthetic: true` flag and
     a note field. Nothing tells Google a price moved when it did not.

The site also carries one line of copy on the price board saying the movement
shown is illustrative until real recording accumulates. That is a sentence in
the board's footnote, not a banner.

TO REPLACE THIS WITH REAL HISTORY
---------------------------------
Delete the file and record actual prices:

    rm build/data/price-history.json
    python3 build/snapshot_prices.py --date 2026-07-01   # a price you know
    python3 build/snapshot_prices.py --date 2026-08-01
    python3 build/snapshot_prices.py                     # today

Real observations and seeded ones use the same format, so they can also be
mixed: seed once, then let snapshot_prices.py append truth on top. Every point
it adds from then on is real.

THE MODEL
---------
Deterministic, seeded from the SKU, so a rebuild produces byte-identical
output — a series that changes every build is useless for reviewing a design
and would make the board lie differently each day.

Every product ends HIGHER than it started, at the owner's instruction. Iranian
parts pricing has drifted upward for years, so a monotone-ish rise is the
plausible shape; the walk still has flat weeks and the occasional small dip
inside the trend, because a series that rises by the same amount every week
looks generated at a glance.
"""
import argparse, datetime, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.join(HERE, "data", "price-history.json")
SRC = os.path.join(HERE, "data", "products.source.json")

# Total rise over the whole window, per SKU, spread across this band. ~14-26%
# over ten weeks is aggressive but it is the right order for this market, and
# it keeps the weekly deltas in the 1-4% range the chips are designed around.
RISE_LO, RISE_HI = 0.14, 0.26


def walk(sku, final, weeks, today):
    """A rising series of [iso_date, rial] ending exactly on `final`."""
    h = hashlib.sha256(sku.encode()).digest()
    total = RISE_LO + (h[0] / 255.0) * (RISE_HI - RISE_LO)
    start = final / (1.0 + total)

    # Weekly step weights from the hash. A weight can be zero (a flat week) or
    # slightly negative (a small correction), but the weights are normalised so
    # the cumulative path still lands on `final`.
    raw = []
    for i in range(weeks - 1):
        b = h[(i * 7 + 3) % len(h)] / 255.0
        w = b - 0.18                      # ~18% of weeks come out negative
        raw.append(max(-0.35, w))
    s = sum(raw) or 1.0
    steps = [w / s for w in raw]

    out, price = [], start
    for i in range(weeks):
        d = today - datetime.timedelta(days=(weeks - 1 - i) * 7)
        if i == weeks - 1:
            price = final                 # land on the real catalogue price
        else:
            if i:
                price = price * (1 + total * steps[i - 1])
            # round to 500 toman = 5000 rial, the way a parts price is quoted
            price = max(5000, round(price / 5000) * 5000)
        out.append([d.isoformat(), int(price)])

    # Collapse consecutive equal prices: that is how snapshot_prices.py stores
    # real observations, so the seeded file has the same shape.
    dedup = [out[0]]
    for row in out[1:]:
        if row[1] != dedup[-1][1]:
            dedup.append(row)
    return dedup


def report():
    if not os.path.isfile(HIST):
        print("no price history on disk")
        return 0
    h = json.load(open(HIST, encoding="utf-8"))
    pts = sum(len(v) for v in h.values())
    multi = sum(1 for v in h.values() if len(v) > 1)
    rising = sum(1 for v in h.values() if len(v) > 1 and v[-1][1] > v[0][1])
    dates = sorted({d for v in h.values() for d, _p in v})
    print(f"  {len(h)} SKUs, {pts} observations, {multi} with a trend")
    print(f"  {rising} of {multi} end higher than they started")
    print(f"  span {dates[0]} .. {dates[-1]}  ({len(dates)} distinct dates)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weeks", type=int, default=12)
    ap.add_argument("--today", default=None, help="ISO date of the last point")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        return report()

    today = (datetime.date.fromisoformat(a.today) if a.today
             else datetime.date.today())
    src = json.load(open(SRC, encoding="utf-8"))
    hist = {}
    for p in src:
        if isinstance(p.get("p"), int):
            # products.source.json stores TOMAN; the history stores RIAL.
            hist[p["s"]] = walk(p["s"], p["p"] * 10, a.weeks, today)
    json.dump(hist, open(HIST, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"wrote {HIST}")
    report()
    print("\n  These numbers are INVENTED. The last point of each series is the"
          "\n  real catalogue price; the path behind it is modelled. See the"
          "\n  module docstring for how to replace it with real observations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
