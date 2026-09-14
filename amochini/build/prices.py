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
            f'<circle class="hc-hit" cx="{x:.1f}" cy="{y:.1f}" r="11" '
            f'fill="transparent" tabindex="0" role="img" '
            f'aria-label="{jalali_str(d)}: {toman(v)} تومان">'
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
