# -*- coding: utf-8 -*-
"""
Price-history statistics and the SVG marks that render them.

Sparklines and history charts are generated as SVG AT BUILD TIME, not drawn by
a charting library in the browser. That keeps the price index at zero JS, zero
layout shift and zero third-party bytes — the same constraints as the rest of
the site — and it means the marks render identically with scripts disabled.

THE HONESTY RULE, and it is not negotiable: nothing here invents a data point.
A product with one observation has no trend, gets no sparkline and no delta —
it renders as a price with the date it was recorded. Drawing a line through a
single point would be inventing price movement, and these are numbers
customers act on. Charts appear only once `snapshot_prices.py` has actually
seen the price change.
"""
import datetime

# Jalali month names, for rendering observation dates to readers.
JALALI_MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                 "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]


def gregorian_to_jalali(g):
    """ISO date string -> (jy, jm, jd). Standard Birashk-style conversion."""
    y, m, d = (int(x) for x in g.split("-"))
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = y - 1600
    gm2 = m - 1
    g_day_no = (365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100
                + (gy2 + 399) // 400 + g_d_m[gm2] + d - 1)
    if gm2 > 1 and ((y % 4 == 0 and y % 100 != 0) or y % 400 == 0):
        g_day_no += 1
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 366) // 365 + 1
        j_day_no = (j_day_no - 366) % 365
    for i in range(11):
        days = 31 if i < 6 else 30
        if j_day_no < days:
            return jy, i + 1, j_day_no + 1
        j_day_no -= days
    return jy, 12, j_day_no + 1


def jalali_str(g, *, with_year=True):
    jy, jm, jd = gregorian_to_jalali(g)
    s = f"{jd} {JALALI_MONTHS[jm - 1]}"
    return f"{s} {jy}" if with_year else s


def stats(series, divisor=10):
    """Derive display stats from a [[iso_date, rial], ...] series.

    `points` is 0 or 1 for anything with no observed movement, and callers must
    treat `direction == "new"` as "no trend exists" rather than as "flat".
    """
    if not series:
        return dict(points=0, direction="none", latest=None)
    latest_date, latest = series[-1]
    out = dict(points=len(series), direction="new", latest=latest,
               latest_date=latest_date, first_date=series[0][0],
               history=series, low=min(p for _d, p in series),
               high=max(p for _d, p in series))
    if len(series) < 2:
        return out
    prev_date, prev = series[-2]
    change = latest - prev
    out.update(prev=prev, prev_date=prev_date, change=change,
               change_pct=(change / prev * 100) if prev else 0.0,
               direction="up" if change > 0 else "down" if change < 0 else "flat",
               # the span the delta is measured over, so the label can name it
               span_days=(datetime.date.fromisoformat(latest_date)
                          - datetime.date.fromisoformat(prev_date)).days)
    return out


def sparkline(series, *, w=72, h=24, up_bad=True):
    """A 12-point sparkline. Returns "" when there is nothing to draw.

    Per the mark spec: a thin 2px line in the de-emphasis hue with the current
    point marked in the direction colour. No axes, no labels — a sparkline is
    shape-only context beside a number that carries the value.
    """
    pts = series[-12:]
    if len(pts) < 2:
        return ""
    vals = [p for _d, p in pts]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    pad = 3
    n = len(vals) - 1
    coords = []
    for i, v in enumerate(vals):
        x = pad + (w - 2 * pad) * (i / n)
        y = pad + (h - 2 * pad) * (1 - (v - lo) / span)
        coords.append((x, y))
    # RTL note: time still runs left->right inside the mark. A sparkline is a
    # picture of a series, not text, and mirroring it would make "rising" read
    # as "falling" to anyone who has seen a chart before.
    d = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}"
                 for i, (x, y) in enumerate(coords))
    rising = vals[-1] > vals[0]
    tone = "var(--px-rise)" if (rising == up_bad) else "var(--px-fall)"
    cx, cy = coords[-1]
    return (
        f'<svg class="spark" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'aria-hidden="true" focusable="false">'
        f'<path d="{d}" fill="none" stroke="var(--spark-ink)" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.6" fill="{tone}"/>'
        f'</svg>')


def history_chart(series, *, up_bad=True, w=520, h=150):
    """A per-product price history chart, as build-time SVG.

    Returns "" for fewer than two observations — a line through one point
    would be an invented trend.

    Chrome, deliberately sparse: no gridlines, no axis spines, and labels only
    on the extremes rather than a number on every point. Each point carries an
    oversized transparent hit circle with an SVG <title>, which gives a native
    browser tooltip on hover and focus at zero JS cost. The visible marks stay
    at the 2px line / >=8px marker spec.
    """
    if len(series) < 2:
        return ""
    vals = [p for _d, p in series]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    padx, padt, padb = 10, 14, 26
    n = len(vals) - 1
    pts = []
    for i, (d, v) in enumerate(series):
        x = padx + (w - 2 * padx) * (i / n)
        y = padt + (h - padt - padb) * (1 - (v - lo) / span)
        pts.append((x, y, d, v))
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}"
                    for i, (x, y, _d, _v) in enumerate(pts))
    base = h - padb
    area = (f"M{pts[0][0]:.1f} {base:.1f} "
            + " ".join(f"L{x:.1f} {y:.1f}" for x, y, _d, _v in pts)
            + f" L{pts[-1][0]:.1f} {base:.1f} Z")
    rising = vals[-1] > vals[0]
    # One colour, two uses. The area under the curve is the stroke colour at
    # 12% alpha rather than a separate pale tint, so the chart adds no value
    # to the palette — DESIGN.md §2 has no chip/fill tints at all. Also works
    # on both grounds, because --px-rise/--px-fall are contextual.
    tone = "var(--px-rise)" if (rising == up_bad) else "var(--px-fall)"
    fill = tone

    def fa(n_):
        return "".join("۰۱۲۳۴۵۶۷۸۹"[int(c)] if c.isdigit() else c for c in str(n_))

    def toman(v):
        return fa(f"{v // 10:,}").replace(",", "٬")

    dots = ""
    for i, (x, y, d, v) in enumerate(pts):
        last = i == len(pts) - 1
        dots += (
            # A hover tooltip, not a tab stop. These circles render at
            # 16-30px depending on the chart's width, under the WCAG 2.5.8
            # 24px minimum, and twelve of them per chart put twelve tiny
            # stops in the tab order. The keyboard and screen-reader route to
            # this data is the full observation table below the chart, which
            # is a real <table> — an equivalent control that meets the size
            # requirement, which is what 2.5.8 asks for.
            f'<circle class="hc-hit" cx="{x:.1f}" cy="{y:.1f}" r="11" '
            f'fill="transparent" aria-hidden="true">'
            f'<title>{jalali_str(d)} — {toman(v)} تومان</title></circle>')
        if last:
            dots += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{tone}" '
                     f'stroke="var(--ground)" stroke-width="2"/>')
    # Selective direct labels: the extremes and the two end dates only.
    labels = (
        f'<text class="hc-y" x="{w - padx}" y="{padt - 3}" text-anchor="end">'
        f'{toman(hi)}</text>'
        f'<text class="hc-y" x="{w - padx}" y="{base - 2}" text-anchor="end">'
        f'{toman(lo)}</text>'
        # text-anchor="middle" for the date labels, not start/end: SVG's
        # start/end resolve against the text's own direction, so in an RTL
        # document they anchored from the wrong side and the first label was
        # clipped off the left of the box. "middle" has no side to get wrong,
        # so the label keeps its RTL word order («۲۳ شهریور», not the reverse)
        # while staying inside the plot.
        f'<text class="hc-x" x="{pts[0][0] + 34:.1f}" y="{h - 8}" text-anchor="middle">'
        f'{fa(jalali_str(series[0][0], with_year=False))}</text>'
        f'<text class="hc-x" x="{pts[-1][0] - 34:.1f}" y="{h - 8}" text-anchor="middle">'
        f'{fa(jalali_str(series[-1][0], with_year=False))}</text>')
    return (
        f'<svg class="hchart" viewBox="0 0 {w} {h}" role="group" '
        f'aria-label="نمودار تغییر قیمت" preserveAspectRatio="none">'
        f'<path d="{area}" fill="{fill}" fill-opacity="0.12" stroke="none"/>'
        f'<path d="{line}" fill="none" stroke="{tone}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'{dots}{labels}</svg>')


def history_table(series):
    """The table view every chart must have. Also the fallback when the chart
    is absent, so the data is always reachable in text."""
    if not series:
        return ""
    def fa(n_):
        return "".join("۰۱۲۳۴۵۶۷۸۹"[int(c)] if c.isdigit() else c for c in str(n_))
    rows = ""
    for i, (d, v) in enumerate(reversed(series)):
        prev = series[len(series) - i - 2][1] if i < len(series) - 1 else None
        if prev is None:
            delta = "نخستین ثبت"
        else:
            ch = v - prev
            sign = "+" if ch > 0 else ""
            delta = (f"{sign}{fa(f'{abs(ch) // 10:,}'.replace(',', chr(0x066C)))}"
                     if ch else "بدون تغییر")
            if ch:
                delta = ("▲ " if ch > 0 else "▼ ") + delta
        rows += (f"<tr><td>{fa(jalali_str(d))}</td>"
                 f"<td>{fa(f'{v // 10:,}'.replace(',', chr(0x066C)))}</td>"
                 f"<td>{delta}</td></tr>")
    return (f'<table class="spec hist-table"><caption>تاریخچه قیمت (تومان)</caption>'
            f'<thead><tr><th scope="col">تاریخ</th><th scope="col">قیمت</th>'
            f'<th scope="col">تغییر</th></tr></thead><tbody>{rows}</tbody></table>')


# ==========================================================================
# THE INDEX
# An exchange has an index. This one is an equal-weighted price index across
# every priced SKU we hold observations for, base 100 at the first date in the
# record.
#
# Equal-weighted, not value-weighted, and the reason is honesty: a
# value-weighted basket needs sales volumes, we have none, and inventing
# weights would make the index a guess dressed as a measurement. Equal weight
# needs nothing but the prices, and it answers the question a parts buyer
# actually has — "have brake parts got more expensive?" — without pretending
# to know what sells.
#
# Carry-forward: a SKU's price on a date is its most recent observation on or
# before that date. That is the standard treatment for an irregular series and
# it is what makes a board of 116 SKUs with different recording dates
# comparable.
# ==========================================================================

def _as_of(series, date):
    """The last observed price on or before `date`, or None."""
    val = None
    for d, p in series:
        if d <= date:
            val = p
        else:
            break
    return val


def index_series(history, *, base_ratio=0.9):
    """{sku: [[date, rial], ...]} -> (series, meta).

    `series` is [[date, index_value], ...] with the base date at 100.0.
    Returns ([], {}) when there is nothing to index.
    """
    if not history:
        return [], {}
    dates = sorted({d for s in history.values() for d, _p in s})
    if not dates:
        return [], {}
    # The base is the first date on which at least `base_ratio` of the SKUs
    # already have a price. Starting at a date where only a handful are
    # recorded would let the index jump on coverage rather than on price.
    n = len(history)
    base = None
    for d in dates:
        have = sum(1 for s in history.values() if _as_of(s, d) is not None)
        if have >= n * base_ratio:
            base = d
            break
    if base is None:
        return [], {}
    basket = {k: _as_of(s, base) for k, s in history.items()}
    basket = {k: v for k, v in basket.items() if v}
    if not basket:
        return [], {}

    series = []
    for d in [x for x in dates if x >= base]:
        rel = []
        for k, b in basket.items():
            cur = _as_of(history[k], d)
            if cur:
                rel.append(cur / b)
        if rel:
            series.append([d, round(100.0 * sum(rel) / len(rel), 2)])

    meta = dict(base_date=base, members=len(basket),
                latest=series[-1][1] if series else 100.0,
                first=series[0][1] if series else 100.0)
    if len(series) > 1:
        meta["change"] = round(series[-1][1] - series[-2][1], 2)
        meta["change_pct"] = round(
            (series[-1][1] - series[-2][1]) / series[-2][1] * 100, 2)
        meta["since_base_pct"] = round(series[-1][1] - 100.0, 2)
        meta["prev_date"] = series[-2][0]
    return series, meta


def breadth(history, date=None, prev=None):
    """How many SKUs rose, fell and held between two dates — market breadth,
    the other number every exchange board carries."""
    dates = sorted({d for s in history.values() for d, _p in s})
    if len(dates) < 2:
        return dict(up=0, down=0, flat=0, total=len(history))
    date = date or dates[-1]
    prev = prev or dates[dates.index(date) - 1]
    up = down = flat = 0
    for s in history.values():
        a, b = _as_of(s, prev), _as_of(s, date)
        if a is None or b is None:
            continue
        if b > a:
            up += 1
        elif b < a:
            down += 1
        else:
            flat += 1
    return dict(up=up, down=down, flat=flat, total=up + down + flat,
                date=date, prev=prev)


def index_chart(series, *, w=1000, h=200):
    """The index chart: shape only, no text.

    Deliberately label-free. The chart is full-bleed inside a column that runs
    from ~350px on a phone to ~570px on a desktop, and an SVG scaled from a
    1000-unit viewBox squashes any text inside it to 6-7px — readable in the
    source, unreadable on screen, and no font-size in SVG can opt out of the
    viewBox scale. The numbers therefore live in real HTML beside the chart
    (index_scale below), where they are real type at a real size.

    Drawn in --ix-ink, contextual like the other chart tokens, and never in a
    direction colour: an index is not good or bad news, it is the level.
    """
    if len(series) < 2:
        return ""
    vals = [v for _d, v in series]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    pad = 6
    n = len(vals) - 1
    pts = []
    for i, (d, v) in enumerate(series):
        x = pad + (w - 2 * pad) * (i / n)
        y = pad + (h - 2 * pad) * (1 - (v - lo) / span)
        pts.append((x, y, d, v))
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}"
                    for i, (x, y, _d, _v) in enumerate(pts))
    area = (f"M{pts[0][0]:.1f} {h:.1f} "
            + " ".join(f"L{x:.1f} {y:.1f}" for x, y, _d, _v in pts)
            + f" L{pts[-1][0]:.1f} {h:.1f} Z")

    def fa(x):
        return "".join("۰۱۲۳۴۵۶۷۸۹"[int(c)] if c.isdigit() else c for c in str(x))

    dots = ""
    for i, (x, y, d, v) in enumerate(pts):
        num = fa(f"{v:.2f}").replace(".", "\u066B")
        # see the note in history_chart: hover tooltip, not a tab stop
        dots += (f'<circle class="hc-hit" cx="{x:.1f}" cy="{y:.1f}" r="14" '
                 f'fill="transparent" aria-hidden="true">'
                 f'<title>{jalali_str(d)} — شاخص {num}</title></circle>')
        if i == len(pts) - 1:
            dots += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" '
                     f'fill="var(--ix-ink)" stroke="var(--ground)" '
                     f'stroke-width="2"/>')
    return (f'<svg class="ixchart" viewBox="0 0 {w} {h}" role="group" '
            f'aria-label="نمودار شاخص قیمت" preserveAspectRatio="none">'
            f'<path d="{area}" fill="var(--ix-ink)" fill-opacity="0.12" stroke="none"/>'
            f'<path d="{line}" fill="none" stroke="var(--ix-ink)" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'vector-effect="non-scaling-stroke"/>'
            f'{dots}</svg>')


def index_scale(series):
    """The chart's axis, as HTML. Real text at a real size — see index_chart."""
    if len(series) < 2:
        return ""
    vals = [v for _d, v in series]

    def fa(x):
        return "".join("۰۱۲۳۴۵۶۷۸۹"[int(c)] if c.isdigit() else c for c in str(x))

    def num(v):
        return fa(f"{v:.2f}").replace(".", "\u066B")
    return (f'<div class="ix-scale">'
            f'<span>{fa(jalali_str(series[0][0], with_year=False))}</span>'
            f'<span class="ix-range">کمترین {num(min(vals))} — '
            f'بیشترین {num(max(vals))}</span>'
            f'<span>{fa(jalali_str(series[-1][0], with_year=False))}</span>'
            f'</div>')


def index_table(series):
    """The index series as a real table — the accessible equivalent of the
    chart, and the reason the chart's points are not tab stops."""
    if len(series) < 2:
        return ""
    def fa(x):
        return "".join("۰۱۲۳۴۵۶۷۸۹"[int(c)] if c.isdigit() else c for c in str(x))
    rows = ""
    prev = None
    for d, v in series:
        chg = "—" if prev is None else fa(f"{v - prev:+.2f}").replace(".", "\u066B")
        rows += (f'<tr><td>{fa(jalali_str(d))}</td>'
                 f'<td>{fa(f"{v:.2f}").replace(".", chr(0x066B))}</td>'
                 f'<td>{chg}</td></tr>')
        prev = v
    return (f'<table class="spec hist-table"><caption>سابقه شاخص</caption>'
            f'<thead><tr><th scope="col">تاریخ</th><th scope="col">شاخص</th>'
            f'<th scope="col">تغییر</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')
