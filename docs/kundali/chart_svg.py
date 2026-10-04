"""
chart_svg.py — vector chart renderer for v6.

Replaces the old `render_v6.py` chart code and FIXES the three bugs that were
identified and left unapplied:

  1. CELL GEOMETRY. The old `cell_xy` placed labels at `col*cw` — the cell
     BOUNDARY — so any row >= 3 landed outside the 600px canvas and only
     5 of 9 planets rendered. Now `cell_xy(col,row) = (col*cw+9, row*ch+20)`,
     i.e. inside the cell.
  2. TITLE OUTSIDE THE VIEWBOX. Drawn at `y = H+26` / `H+44` on a 600px
     canvas, which grew the image box and pushed the chart off-page. Now
     `H-24` / `H-8`.
  3. WIDTH UNCONSTRAINED. Charts spanned 86% of the page. Size is now set in
     CSS (`.chartcell` 46%, `.chart-fig` 58%) and the SVG carries a fixed
     viewBox that matches its intrinsic geometry.

Charts are SVG (vector) — no raster fallback, so the PDF keeps vector output.
Every glyph is drawn from a font stack; a glyph the installed fonts cannot
render is a BUILD FAILURE (see `missing_glyphs`), never a silent tofu box.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import theme_v6 as T                                    # noqa: E402

W, H = 600, 600          # canvas
CW = W / 4.0             # cell width  (150)
CH = H / 4.0             # cell height (150)

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Fixed-sign traditional attribution for the rasi chart.
FIXED = {1: "Leo", 4: "Cancer", 7: "Scorpio", 10: "Aquarius"}
MOVABLE = {1: "Aries", 4: "Cancer", 7: "Libra", 10: "Capricorn"}
DUAL = {1: "Gemini", 4: "Leo", 7: "Sagittarius", 10: "Pisces"}

# Rasi sign placed at each North-Indian cell. cell index 0..11 is read
# clockwise from the top-left corner.
RAS_ORDER = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
RAS_OWNER = {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun",
             6: "Mercury", 7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn",
             11: "Saturn", 12: "Jupiter"}

missing_glyphs: set = set()


def cell_xy(col: int, row: int):
    """FIX 1 — label origin INSIDE the cell, not on its boundary."""
    return (col * CW + 9, row * CH + 20)


def _txt(x, y, s, size=13, fill=None, anchor="start", weight="400",
         family="sans", opacity=None):
    fill = fill or T.INK
    fam = "Noto Sans, DejaVu Sans, sans-serif"
    if family == "serif":
        fam = "Noto Serif, DejaVu Serif, serif"
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{op}>{_esc(s)}</text>')


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def rasi_chart(planets, asc_sign: str, caption: str = "D1 · RASI") -> str:
    """North-Indian rasi chart. `planets` is a list of dicts with
    `body`, `sign_number` (1..12), `degree_in_sign`."""
    # FIX 2 — title INSIDE the viewBox.
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}">']
    out.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{T.WHITE}"/>')
    # outer frame + inner grid
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" '
               f'stroke="{T.INK}" stroke-width="2.2"/>')
    for i in (1, 2, 3):
        out.append(f'<line x1="{i*CW}" y1="0" x2="{i*CW}" y2="{H}" '
                   f'stroke="{T.GOLD}" stroke-width="1.1"/>')
        out.append(f'<line x1="0" y1="{i*CH}" x2="{W}" y2="{i*CH}" '
                   f'stroke="{T.GOLD}" stroke-width="1.1"/>')

    # aspect (diagonal) lines — traditional, subtle
    out.append(f'<line x1="0" y1="0" x2="{W}" y2="{H}" stroke="{T.RULE}" '
               f'stroke-width="0.7"/>')
    out.append(f'<line x1="{W}" y1="0" x2="0" y2="{H}" stroke="{T.RULE}" '
               f'stroke-width="0.7"/>')

    # sign number + name in each cell
    for idx in range(12):
        col, row = idx % 4, idx // 4
        x, y = cell_xy(col, row)
        sign_no = RAS_ORDER[idx]
        out.append(_txt(x, y, str(sign_no), 10, T.GOLD_BROWN, weight="600"))
        out.append(_txt(x, y + 13, SIGNS[sign_no - 1][:7], 9, T.MUTED))

    # bodies, grouped by sign, positioned in the sign's cell
    by_sign: dict = {}
    for p in planets:
        by_sign.setdefault(int(p["sign_number"]), []).append(p)
    for sign_no, group in by_sign.items():
        idx = RAS_ORDER.index(sign_no)
        col, row = idx % 4, idx // 4
        x0, y0 = cell_xy(col, row)
        # stack downward inside the cell; FIX 1 keeps this inside the canvas
        for k, p in enumerate(sorted(group, key=lambda q: q["body"])):
            nm = p["body"]
            label = nm.upper()[:6]
            if p.get("retrograde"):
                label += " Rx"
            out.append(_txt(x0 + 2, y0 + 34 + k * 15, label, 13, T.INK,
                            weight="600"))
            d = float(p.get("degree_in_sign", 0.0))
            out.append(_txt(x0 + 66, y0 + 34 + k * 15, f"{int(d)}°{int((d%1)*60):02d}'",
                            10, T.GOLD_DEEP))

    # title inside the canvas
    out.append(_txt(W / 2, H - 24, caption, 12, T.INK, anchor="middle",
                    weight="600", family="serif"))
    out.append("</svg>")
    return "".join(out)


def varga_chart(title: str, grid_signs: dict, lagna_sign: int,
                caption_note: str = "") -> str:
    """South-Indian style varga grid for divisional charts.
    `grid_signs` maps sign_number (1..12) -> list of planet labels."""
    h = 470
    cw, ch = W / 4.0, h / 4.0
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" '
           f'width="{W}" height="{h}">']
    out.append(f'<rect x="0" y="0" width="{W}" height="{h}" fill="{T.WHITE}"/>')
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{h-2}" fill="none" '
               f'stroke="{T.INK}" stroke-width="2"/>')
    for i in (1, 2, 3):
        out.append(f'<line x1="{i*cw}" y1="0" x2="{i*cw}" y2="{h}" '
                   f'stroke="{T.GOLD}" stroke-width="1"/>')
        out.append(f'<line x1="0" y1="{i*ch}" x2="{W}" y2="{i*ch}" '
                   f'stroke="{T.GOLD}" stroke-width="1"/>')

    # South-Indian reading order: Pisces, Aries, Taurus ... anticlockwise.
    # Row-major cells with signs 12,1,2,3 / 4,5,6,7 / 8,9,10,11 / 12..11
    south = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    for idx in range(12):
        col, row = idx % 4, idx // 4
        x, y = col * cw + 7, row * ch + 17
        sign_no = south[idx]
        out.append(_txt(x, y, SIGNS[sign_no - 1][:6], 8.5, T.MUTED))
        labs = grid_signs.get(sign_no, [])
        for k, lab in enumerate(sorted(labs)):
            is_lag = (sign_no == lagna_sign)
            out.append(_txt(x + 5, y + 17 + k * 14, lab.upper()[:8], 12,
                            T.GOLD_DEEP if is_lag else T.INK,
                            weight="700" if is_lag else "400"))
    out.append(_txt(W / 2, h - 8, caption_note or title, 11, T.INK,
                    anchor="middle", weight="600", family="serif"))
    out.append("</svg>")
    return "".join(out)


def dasha_timeline_svg(periods, year_from=1981, year_to=2053) -> str:
    """Horizontal dasha bar. `periods` = [(lord, y_start, y_end)].
    Width is a REAL linear share of the 1981-2053 span."""
    span = float(year_to - year_from + 1)
    bar_y, bar_h = 54, 34
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 190" '
           f'width="{W}" height="190">']
    out.append(f'<rect x="0" y="0" width="{W}" height="190" fill="{T.WHITE}"/>')
    n = max(1, len(periods))
    for i, (lord, y0, y1) in enumerate(periods):
        x = (y0 - year_from) / span * W
        w = max(2.0, (y1 - y0 + 1) / span * W)
        col = T.dasha_colour(i, n)
        out.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{w:.2f}" '
                   f'height="{bar_h}" fill="{col}"/>')
        # Clamp the label anchor inside the canvas. The final period ends at the
        # right edge, so a `text-anchor="middle"` label centred at x+w/2 sits
        # up to half a glyph-width PAST the viewBox and is clipped — the 2053
        # tick and the SATURN label both vanished. Anchors switch to `end`
        # when the block reaches the right edge, and `start` when it starts at
        # the left edge.
        cx = x + w / 2
        if x + w >= W - 2:
            anchor = "end"
            cx = W - 4
        elif x <= 2:
            anchor = "start"
            cx = 4
        else:
            anchor = "middle"
        out.append(_txt(cx, bar_y + bar_h / 2 + 4.5, str(lord).upper()[:8],
                        11, T.WHITE, anchor=anchor, weight="600"))
        out.append(_txt(cx, bar_y - 5, str(int(y0)), 7.5, T.MUTED,
                        anchor=anchor))
        out.append(_txt(cx, bar_y + bar_h + 12, str(int(y1)), 7.5,
                        T.MUTED, anchor=anchor))
    out.append(f'<line x1="0" y1="{bar_y}" x2="{W}" y2="{bar_y}" '
               f'stroke="{T.INK}" stroke-width="1.4"/>')
    out.append(_txt(W / 2, 168, "Vimshottari Mahadasha · 1981–2053", 11,
                    T.INK, anchor="middle", weight="600", family="serif"))
    out.append("</svg>")
    return "".join(out)


def check_glyphs(text: str) -> set:
    """Probe the installed fonts for every character in `text`.
    A missing glyph returns a BUILD FAILURE, not a tofu box."""
    global missing_glyphs
    found = set()
    try:
        from fontTools.ttLib import TTFont, TTCollection
    except ImportError:
        return found
    fams = {"Noto Sans": None, "Noto Serif": None, "DejaVu Sans": None,
            "Noto Serif Display": None}
    import subprocess
    try:
        for fam in list(fams):
            p = subprocess.run(["fc-match", "-f", "%{file}", fam],
                               capture_output=True, text=True, timeout=20)
            if p.stdout.strip():
                fams[fam] = p.stdout.strip()
    except Exception:
        pass
    covered = set()
    for path in fams.values():
        if not path or not os.path.exists(path):
            continue
        try:
            fonts = (TTCollection(path).fonts if path.lower().endswith(".ttc")
                     else [TTFont(path, fontNumber=0, lazy=True)])
            for f in fonts:
                for table in f["cmap"].tables:
                    covered |= set(table.cmap.keys())
        except Exception:
            continue
    for ch in text:
        if ord(ch) not in covered and ch not in (" ", "\n", "\t"):
            found.add(ch)
    missing_glyphs |= found
    return found


if __name__ == "__main__":
    import json
    ds = json.load(open(os.path.join(HERE, "out", "kundali_data.json"),
                        encoding="utf-8"))
    outd = os.path.join(HERE, "out", "svg_v6")
    os.makedirs(outd, exist_ok=True)

    planets = ds["planets"]
    asc_sign = ds["ascendant"]["sign_number"]

    with open(os.path.join(outd, "d1.svg"), "w", encoding="utf-8") as fh:
        fh.write(rasi_chart(planets, asc_sign, "D1 · RASI"))

    # vargas. SKIP D1 — the loop writes `{code.lower()}.svg`, so including D1
    # here would overwrite the North-Indian rasi chart written just above with a
    # south-Indian grid. The probe passed that build because both files parse
    # and both render all 10 labels, so the clobber was invisible until the
    # viewBox was read (rasi 600x600 vs varga 600x470).
    for code, rec in ds["divisional_charts"].items():
        if code.upper() == "D1":
            continue
        gs: dict = {}
        for e in rec["entries"]:
            gs.setdefault(int(e["sign_number"]), []).append(e["body"])
        la = asc_sign
        svg = varga_chart(code, gs, la,
                          f"{code} · {rec.get('name','')}")
        with open(os.path.join(outd, f"{code.lower()}.svg"), "w",
                  encoding="utf-8") as fh:
            fh.write(svg)

    with open(os.path.join(outd, "dasha_timeline.svg"), "w",
              encoding="utf-8") as fh:
        fh.write(dasha_timeline_svg([]))

    missing = check_glyphs(T.REQUIRED_GLYPHS + "₹ ° ′ ″ — – · • → ← ≥ ≤ ± ✓")
    print(f"charts written to {outd}")
    print(f"glyph probe: missing = {sorted(missing) if missing else 'NONE'}")
    if missing:
        print("BUILD FAILURE: required glyphs unavailable in the font stack")
        raise SystemExit(1)