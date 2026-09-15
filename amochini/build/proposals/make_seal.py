"""Build the 刹车 seal as pure SVG paths — no CJK webfont ships."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
TEXT = "刹车"
BOX, CELL, GUT = 52.0, 19.0, 3.0

def build(amber="#f7ae0c"):
    f = TTFont(FONT, fontNumber=0)
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    ds, bounds = [], []
    for ch in TEXT:
        g = gs[cmap[ord(ch)]]
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.0f}"); g.draw(pen)
        bp = BoundsPen(gs); g.draw(bp)
        ds.append(pen.getCommands()); bounds.append(bp.bounds)
    x0 = min(b[0] for b in bounds); x1 = max(b[2] for b in bounds)
    y0 = min(b[1] for b in bounds); y1 = max(b[3] for b in bounds)
    s = CELL / (x1 - x0)
    inkw = CELL * 2 + GUT
    left = (BOX - inkw) / 2
    # centre the INK box vertically, not the em box: a CJK glyph's em box is
    # taller than its ink and the seal reads visibly high if you trust it.
    ybase = BOX / 2 + (y1 + y0) / 2 * s
    out = [f'<path transform="translate({left + i*(CELL+GUT) - x0*s:.2f},'
           f'{ybase:.2f}) scale({s:.5f},{-s:.5f})" d="{d}"/>'
           for i, d in enumerate(ds)]
    return (f'<svg viewBox="0 0 {BOX:.0f} {BOX:.0f}" aria-hidden="true">'
            f'<rect x="1.4" y="1.4" width="{BOX-2.8:.1f}" height="{BOX-2.8:.1f}" rx="2" '
            f'fill="none" stroke="{amber}" stroke-width="2.6"/>'
            f'<g fill="{amber}">{"".join(out)}</g></svg>')

if __name__ == "__main__":
    svg = build()
    open("seal.svg", "w").write(svg)
    print(len(svg), "bytes")
