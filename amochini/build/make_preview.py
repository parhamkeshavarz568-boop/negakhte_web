#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a THROWAWAY preview of the price index with synthetic history, so the
design can be reviewed before real snapshots exist.

    python3 build/make_preview.py            # -> /tmp/amochini-preview

NOTHING THIS WRITES IS EVER PUBLISHED. It builds to a temp directory with a
temp history file; public/ and build/data/price-history.json are untouched.
Every page it produces carries a loud banner saying the movement is
illustrative, so a screenshot of it can never be mistaken for the real site.

Its only job is to answer "what will this look like in a month".
"""
import json, os, subprocess, sys, tempfile, datetime, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.environ.get("PREVIEW_DIR", "/tmp/amochini-preview")


def deterministic_walk(sku, base, weeks=10):
    """A repeatable pseudo-random walk. Seeded from the SKU so the preview is
    identical every run — a preview that changes each time is useless for
    comparing a design change."""
    h = hashlib.sha256(sku.encode()).digest()
    today = datetime.date(2026, 9, 14)
    # A third of SKUs end on a DECREASE, so the preview exercises both
    # directions and the reviewer can see the blue state and the
    # "biggest decrease" tile. Real data will be whatever it is.
    ends_down = (h[0] % 3 == 0)
    price = int(base * (0.80 if not ends_down else 1.14))
    out = []
    for i in range(weeks):
        d = today - datetime.timedelta(days=(weeks - 1 - i) * 7)
        # Iranian parts pricing drifts upward, with occasional corrections.
        bias = -0.30 if not ends_down else -0.62
        step = (h[i % len(h)] / 255.0 + bias) * 0.055
        price = max(1000, int(price * (1 + step)))
        if i == weeks - 1:
            price = base                     # land exactly on the real price
        out.append([d.isoformat(), price])
    # collapse consecutive equal prices, matching the real storage shape
    dedup = [out[0]]
    for r in out[1:]:
        if r[1] != dedup[-1][1]:
            dedup.append(r)
    return dedup


def main():
    src = json.load(open(os.path.join(HERE, "data", "products.source.json"),
                         encoding="utf-8"))
    hist = {p["s"]: deterministic_walk(p["s"], p["p"])
            for p in src if isinstance(p["p"], int)}
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                      encoding="utf-8")
    json.dump(hist, tmp, ensure_ascii=False)
    tmp.close()

    env = dict(os.environ, PUBLISH_DIR=OUT, PRICE_HISTORY=tmp.name,
               PREVIEW_BANNER="1")
    os.makedirs(OUT, exist_ok=True)
    # assets the preview needs, copied from the real build
    for sub in ("assets", "favicon.svg", "favicon.ico"):
        s_ = os.path.join(ROOT, "public", sub)
        d_ = os.path.join(OUT, sub)
        if os.path.isdir(s_):
            subprocess.run(["cp", "-r", s_, OUT], check=False)
        elif os.path.exists(s_):
            subprocess.run(["cp", s_, d_], check=False)
    r = subprocess.run([sys.executable, os.path.join(HERE, "build.py")],
                       env=env, capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    os.unlink(tmp.name)
    pts = sum(len(v) for v in hist.values())
    print(f"\nPREVIEW ONLY -> {OUT}")
    print(f"  {pts} synthetic observations across {len(hist)} SKUs")
    print(f"  public/ and build/data/price-history.json were NOT touched")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
