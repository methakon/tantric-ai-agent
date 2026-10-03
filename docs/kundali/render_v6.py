"""
render_v6.py — PDF PRESENTATION layer for v6.

SEPARATE FROM THE ASTROLOGY ENGINE BY DESIGN. This module consumes the frozen
validated datasets and the year-wise markdown produced by render_years.py. It
computes no chart position, no dasha and no risk score. Every number it prints
is read from those files.

Fixes over v5
-------------
1. UNICODE. v5 handed WeasyPrint an HTML FRAGMENT with no charset
   declaration, so it defaulted to latin-1 and every em dash, middle dot and
   emoji became mojibake ("â€”", "Â·", "ðŸŸ¡"). Here the document is always a
   COMPLETE html5 document with an explicit UTF-8 meta charset and an explicit
   font stack. Verified: the source .md already carries 0 mojibake, so this is
   purely a pipeline fix.
2. FONT. Measured with fontTools rather than assumed:
       DejaVuSans        18/23 required glyphs  <- best single font
       DejaVuSerif       16/23
       NotoSans          12/23
       NotoSansSymbols2   6/23
   No installed font carries the four colour-emoji codepoints, and NOT ONE font
   covers all required glyphs, so the stack declares a fallback chain per family
   and NO EMOJI ARE USED ANYWHERE. Risk status is rendered as a VECTOR BADGE.
3. RISK STATUS. Previously plain text "YELLOW (emoji CAUTION)". Now a rounded
   vector card with a real background colour per level.
4. CHARTS. v5 emitted 560x560 px SVGs that WeasyPrint scaled to full page
   width, so the D9 dominated its page. Charts are now emitted at a fixed
   target width (a fraction of the usable page), with the caption beneath, and
   are constrained in CSS so they cannot exceed the box.
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kundali_core as K                                   # noqa: E402
import year_engine as YE                                   # noqa: E402

OUT = os.path.join(HERE, "out")

# ----------------------------------------------------------------- design system
FONT_SANS = ("'DejaVu Sans', 'Noto Sans', 'Liberation Sans', sans-serif")
FONT_SERIF = ("'DejaVu Serif', 'Noto Serif', 'Liberation Serif', serif")
FONT_MONO = ("'DejaVu Sans Mono', 'Noto Sans Mono', monospace")

INK = "#1a1a1a"
INK_SOFT = "#4a4a4a"
RULE = "#c8b88a"          # muted gold rule
ACCENT = "#8a6d1f"        # traditional gold
PANEL = "#fbf8f1"         # warm paper panel
PANEL_EDGE = "#ddd0a8"

RISK_STYLE = {
    "GREEN":  {"bg": "#e6f4ea", "edge": "#2e7d32", "dot": "#2e7d32",
               "sub": "LOW / NORMAL", "ink": "#1b5e20"},
    "YELLOW": {"bg": "#fdf6e3", "edge": "#b8860b", "dot": "#c9930a",
               "sub": "CAUTION", "ink": "#7a5c00"},
    "ORANGE": {"bg": "#fdf0e6", "edge": "#c2620a", "dot": "#d4740f",
               "sub": "ELEVATED", "ink": "#8a4400"},
    "RED":    {"bg": "#fdecec", "edge": "#b32020", "dot": "#c62828",
               "sub": "EXTREME ATTENTION", "ink": "#8c1414"},
}

CHART_W = 300          # px; ~62% of the 484px usable A4 width at 96dpi
SVG_PX = 900           # render resolution, downscaled by CSS


def esc(s: str) -> str:
    return _html.escape(str(s), quote=True)


# ------------------------------------------------------------------- risk badge
def risk_badge(level: str, word: str = "", extra: str = "") -> str:
    """Vector status card. NO EMOJI - colour is carried by a CSS background and
    a drawn dot, so it cannot depend on font glyph coverage."""
    st = RISK_STYLE.get(level.upper(), RISK_STYLE["YELLOW"])
    sub = st["sub"] if not word else f"{st['sub']} / {word.upper()}"
    tail = f'<div class="badge-extra">{esc(extra)}</div>' if extra else ""
    return (
        f'<div class="badge" style="background:{st["bg"]};'
        f'border:1.2pt solid {st["edge"]};">'
        f'<span class="badge-dot" style="background:{st["dot"]};"></span>'
        f'<span class="badge-level" style="color:{st["ink"]};">{esc(level.upper())}</span>'
        f'<span class="badge-sub">{esc(sub)}</span>'
        f'{tail}</div>')


# ---------------------------------------------------------------------- charts
def north_indian_svg(lagna_sign: int, placements: dict, title: str,
                      subtitle: str = "") -> str:
    """North-Indian diamond grid. Fixed internal coordinate system; the CSS
    controls display size so the SVG never drives page layout."""
    W = H = 600
    cells = [(4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (1, 5), (2, 6),
             (3, 7), (4, 8), (3, 9), (2, 10), (1, 11)]
    cw = ch = W / 4.0
    glyph = {"Aries": "Ar", "Taurus": "Ta", "Gemini": "Ge", "Cancer": "Cn",
             "Leo": "Le", "Virgo": "Vi", "Libra": "Li", "Scorpio": "Sc",
             "Sagittarius": "Sg", "Capricorn": "Cp", "Aquarius": "Aq",
             "Pisces": "Pi"}
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="DejaVu Sans, Noto Sans, sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#fffdf8"/>',
         f'<rect x="3" y="3" width="{W-6}" height="{H-6}" fill="none" '
         f'stroke="#1a1a1a" stroke-width="2.4"/>',
         f'<path d="M {W/2},3 L {W-3},{H/2} L {W/2},{H-3} L 3,{H/2} Z" '
         f'fill="none" stroke="#1a1a1a" stroke-width="1.5"/>']
    for i in range(1, 4):
        o.append(f'<line x1="{i*cw}" y1="0" x2="{i*cw}" y2="{H}" '
                 f'stroke="#d8d8d8" stroke-width="0.7"/>')
        o.append(f'<line x1="0" y1="{i*ch}" x2="{W}" y2="{i*ch}" '
                 f'stroke="#d8d8d8" stroke-width="0.7"/>')
    for off, (col, row) in enumerate(cells):
        sign = K.SIGNS[(lagna_sign + off) % 12]
        x, y = col * cw, row * ch
        tx, ty = x + 9, y + 20
        o.append(f'<text x="{tx}" y="{ty}" font-size="15" fill="{ACCENT}" '
                 f'font-weight="bold">{glyph[sign]}</text>')
        occ = placements.get(sign, [])
        for j, (name, deg) in enumerate(occ):
            # explicit fill + size so no label can render white-on-white
            o.append(f'<text x="{tx}" y="{ty + 17*(j+1)}" font-size="15" '
                     f'fill="#101010" font-weight="bold">{esc(name)} '
                     f'{deg:.2f}°</text>')
    # lagna marker
    o.append(f'<text x="{W/2}" y="{H+26}" font-size="17" fill="#1a1a1a" '
             f'text-anchor="middle" font-weight="bold">{esc(title)}</text>')
    if subtitle:
        o.append(f'<text x="{W/2}" y="{H+44}" font-size="13" fill="{INK_SOFT}" '
                 f'text-anchor="middle">{esc(subtitle)}</text>')
    o.append('</svg>')
    return "\n".join(o)


def chart_block(div: dict, key: str, asc_sign: int) -> str:
    entries = div.get("entries", [])
    lag = None
    for e in entries:
        b = (e.get("body") or "")
        if b.lower().startswith("lagn") or b == "Ascendant":
            lag = e.get("sign")
            break
    lag = lag or K.SIGNS[asc_sign]
    lsign = K.SIGNS.index(lag)
    pl: dict = {}
    for e in entries:
        body = e.get("body")
        sign = e.get("sign")
        if not body or not sign or body == "Ascendant":
            continue
        pl.setdefault(sign, []).append(
            (body, e.get("degree_in_sign") or 0.0))
    svg = north_indian_svg(
        lsign, pl, f"{key} · {div.get('name', key)}",
        f"lagna {lag} · {len(entries)} bodies · whole-sign")
    svg_name = f"svg_v6/{key.lower()}.svg"
    with open(os.path.join(OUT, svg_name), "w", encoding="utf-8") as fh:
        fh.write(svg)
    return (f'<figure class="chart"><img src="{svg_name}" '
            f'alt="{key} chart" width="{CHART_W}">'
            f'<figcaption>{key} · {esc(div.get("name", key))} — lagna '
            f'{esc(lag)}, {len(entries)} bodies, whole-sign houses</figcaption>'
            f'</figure>')


# ------------------------------------------------------------------ doc builder
class Doc:
    def __init__(self):
        self.buf: list[str] = []

    def h1(self, t):
        self.buf.append(f'<h1>{esc(t)}</h1>')

    def h2(self, t):
        self.buf.append(f'<h2>{esc(t)}</h2>')

    def p(self, t=""):
        self.buf.append(f'<p>{esc(t)}</p>')

    def raw(self, t):
        self.buf.append(t)

    def table(self, headers, rows, cls=""):
        h = "".join(f"<th>{esc(x)}</th>" for x in headers)
        body = []
        for r in rows:
            body.append("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>")
        self.buf.append(f'<table class="{cls}"><thead><tr>{h}</tr></thead>'
                        f'<tbody>{"".join(body)}</tbody></table>')

    def write(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self.buf))


CSS = """
@page {
  size: A4 portrait;
  margin: 16mm 15mm 17mm 15mm;
  @bottom-center { content: counter(page); font-size: 7.5pt; color: #666; }
  @top-right  { content: "Swarna Sekhar Dhar · Vedic Dossier";
                font-size: 7pt; color: #888; }
}
* { box-sizing: border-box; }
body {
  font-family: __FONT_SANS__;
  font-size: 8.6pt; line-height: 1.42; color: __INK__; margin: 0;
}
h1 {
  font-family: __FONT_SERIF__; font-size: 15pt; color: #6b5410;
  border-bottom: 1.6pt solid __RULE__; padding-bottom: 3pt;
  margin: 0 0 8pt 0; page-break-after: avoid; letter-spacing: .2pt;
}
h2 {
  font-family: __FONT_SERIF__; font-size: 10.6pt; color: #6b5410;
  margin: 10pt 0 4pt 0; page-break-after: avoid;
  border-left: 3pt solid __RULE__; padding-left: 5pt;
}
p { margin: 0 0 4pt 0; orphans: 2; widows: 2; }
table {
  border-collapse: collapse; width: 100%; margin: 5pt 0 7pt 0;
  font-size: 7.6pt; page-break-inside: avoid;
}
th {
  background: __PANEL__; color: #4a3a08; text-align: left;
  border: .5pt solid __PANEL_EDGE__; padding: 2.4pt 3.4pt; font-weight: bold;
}
td { border: .4pt solid #ddd6c0; padding: 2.2pt 3.4pt; vertical-align: top; }
tbody tr:nth-child(even) { background: #faf8f2; }
figure.chart {
  margin: 7pt auto 9pt auto; text-align: center;
  page-break-inside: avoid; break-inside: avoid;
}
figure.chart img {
  width: __CHART_W__px; height: auto; max-width: 100%;
  border: .8pt solid __PANEL_EDGE__; background: #fffdf8;
}
figcaption {
  font-size: 7.2pt; color: __INK_SOFT__; margin-top: 3pt;
  font-family: __FONT_SANS__;
}
.badge {
  display: block; border-radius: 5pt; padding: 6pt 9pt;
  margin: 6pt 0 8pt 0; page-break-inside: avoid;
}
.badge-dot {
  display: inline-block; width: 8pt; height: 8pt; border-radius: 50%;
  margin-right: 6pt; vertical-align: middle;
}
.badge-level {
  font-family: __FONT_SERIF__; font-size: 11pt; font-weight: bold;
  letter-spacing: .8pt; vertical-align: middle;
}
.badge-sub {
  display: inline-block; margin-left: 7pt; font-size: 8pt;
  color: __INK_SOFT__; vertical-align: middle;
}
.badge-extra { font-size: 7.4pt; color: __INK_SOFT__; margin-top: 3pt; }
.cover-title {
  font-family: __FONT_SERIF__; font-size: 25pt; color: #6b5410;
  text-align: center; margin: 26pt 0 4pt 0; letter-spacing: .5pt;
}
.cover-sub { text-align: center; font-size: 11pt; color: __INK_SOFT__;
             margin-bottom: 20pt; }
.notice { background: __PANEL__; border-left: 3pt solid __ACCENT__;
          padding: 7pt 10pt; margin: 7pt 0; font-size: 8pt; }
.toc td:first-child { width: 34pt; text-align: right; color: #6b5410;
                      font-weight: bold; }
.year { page-break-before: always; }
.year h1 { font-size: 13.4pt; }
.grid2 { display: flex; gap: 8pt; }
code, .mono { font-family: __FONT_MONO__; font-size: 7.4pt; }
"""


def build_html(body: str, title: str) -> str:
    css = (CSS.replace("__FONT_SANS__", FONT_SANS)
              .replace("__FONT_SERIF__", FONT_SERIF)
              .replace("__FONT_MONO__", FONT_MONO)
              .replace("__INK__", INK)
              .replace("__INK_SOFT__", INK_SOFT)
              .replace("__RULE__", RULE)
              .replace("__ACCENT__", ACCENT)
              .replace("__PANEL__", PANEL)
              .replace("__PANEL_EDGE__", PANEL_EDGE)
              .replace("__CHART_W__", str(CHART_W)))
    # EXPLICIT charset + language. v5 omitted the charset entirely and WeasyPrint
    # fell back to latin-1, which is what produced the mojibake.
    return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            f'<meta charset="utf-8">\n'
            f'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n'
            f'<title>{esc(title)}</title>\n<style>{css}</style>\n</head>\n'
            f'<body>\n{body}\n</body>\n</html>')