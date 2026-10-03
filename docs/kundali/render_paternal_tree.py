"""
render_paternal_tree.py — vector lineage diagram for the final PDF.

Honesty rules baked into the rendering:
  * CONFIRMED names (self, father, grandfather, sons) render in a solid box.
  * Names that exist ONLY as an unverified screenshot transcription render
    DASHED with a [?] marker, so an uncertain reading can never be mistaken for
    a confirmed one on the page.
  * Every ancestor is annotated DOB UNKNOWN, because no ancestor birth date is
    known. Nothing is invented to fill a box.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# (label, confidence, spouse_or_None, note)
LINE = [
    ("Machiram Dhar",  "UNCLEAR",  None,           "DOB unknown · screenshot reads 'Muchiram'"),
    ("Kinkar Dhar",    "PROBABLE", None,           "DOB unknown · spouse not recorded"),
    ("Lakshmik Dhar",  "UNCLEAR",  "Madhobi",      "DOB unknown · screenshot reads 'Lakshmi k'"),
    ("Invar C Dhar",   "UNCLEAR",  "chandra m",    "DOB unknown · screenshot reads 'Isvar C'"),
    ("Shobhi B Dhar",  "PARTIAL",  "Nagendra b",   "DOB unknown · screenshot reads 'Shoshi b'"),
    ("Sisir Kumar Dhar", "CONFIRMED", "Pramila Bala Dhar", "DOB unknown · spouse HIGH"),
    ("Kusankur Dhar",  "CONFIRMED", "Mitra Dhar",  "DOB UNRESOLVED · died 21-Jun-2019"),
    ("Swarna Sekhar Dhar", "CONFIRMED", None,       "b. 09-Dec-1981 01:00 IST"),
]

SONS = [("Sastav Dhar", "b. 02-Apr-2019 16:09 IST"),
        ("Abhyant Dhar", "b. 19-Aug-2021 16:01 IST")]

BOX_W, BOX_H = 268, 62
GAP = 34
LEFT = 60
SPOUSE_X = LEFT + BOX_W + 46
ROW_H = BOX_H + GAP


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    n = len(LINE)
    width = 800
    oy = 84            # top offset for the title block
    sons_gap = 44      # vertical space between the last ancestor and the sons
    footer_lines = 3
    # Height must cover: title block + lineage rows + sons block + footer.
    # The earlier value omitted the sons' box height and the footer, so both were
    # clipped off the bottom of the canvas.
    lineage_bottom = oy + (n - 1) * ROW_H + BOX_H
    sons_top = lineage_bottom + sons_gap
    sons_bottom = sons_top + BOX_H
    height = sons_bottom + 34 + footer_lines * 16 + 18

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
               f'height="{height}" viewBox="0 0 {width} {height}" '
               f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif">')
    out.append('<rect width="100%" height="100%" fill="#fbfaf7"/>')
    out.append(f'<text x="{LEFT}" y="34" font-size="17" font-weight="700" '
               f'fill="#1a1a1a">PATERNAL LINE — SEVEN GENERATIONS</text>')
    out.append(f'<text x="{LEFT}" y="55" font-size="11.5" fill="#666">'
               f'Solid box = confirmed relationship · Dashed box = name from an unverified '
               f'screenshot transcription · [?] = spelling uncertain</text>')

    cx = LEFT + BOX_W / 2
    cy = oy + BOX_H / 2

    for i, (name, conf, spouse, note) in enumerate(LINE):
        x, y = LEFT, oy + i * ROW_H
        confirmed = conf == "CONFIRMED"
        stroke = "#1f4e79" if confirmed else "#8a6d3b"
        dash = '' if confirmed else ' stroke-dasharray="5,3"'
        fill = "#eaf1f8" if confirmed else "#fdf6e8"

        if i < n - 1:
            y1 = y + BOX_H
            y2 = oy + (i + 1) * ROW_H
            out.append(f'<line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2}" '
                       f'stroke="#5a5a5a" stroke-width="1.6" '
                       f'marker-end="url(#ar)"/>')
            out.append(f'<text x="{cx + 7}" y="{(y1 + y2) / 2 + 4}" '
                       f'font-size="9.5" fill="#777">child of</text>')

        out.append(f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" '
                   f'rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.7"{dash}/>')
        marker = '' if confirmed else '  [?]'
        out.append(f'<text x="{x + 13}" y="{y + 25}" font-size="13.5" '
                   f'font-weight="600" fill="#111">{esc(name)}{marker}</text>')
        out.append(f'<text x="{x + 13}" y="{y + 42}" font-size="10" '
                   f'fill="#555">{esc(note)}</text>')
        out.append(f'<text x="{x + 13}" y="{y + 55}" font-size="9" '
                   f'fill="#888">confidence: {esc(conf)}</text>')

        if spouse:
            sx, sy = SPOUSE_X, y
            out.append(f'<line x1="{x + BOX_W}" y1="{y + BOX_H / 2}" '
                       f'x2="{sx}" y2="{sy + BOX_H / 2}" stroke="#a08a5a" '
                       f'stroke-width="1.3"/>')
            out.append(f'<rect x="{sx}" y="{sy}" width="{190}" height="{BOX_H}" '
                       f'rx="5" fill="#f7f2e6" stroke="#a08a5a" '
                       f'stroke-width="1.3" stroke-dasharray="4,3"/>')
            out.append(f'<text x="{sx + 11}" y="{sy + 24}" font-size="11.5" '
                       f'fill="#333">spouse: {esc(spouse)}</text>')
            out.append(f'<text x="{sx + 11}" y="{sy + 41}" font-size="9" '
                       f'fill="#888">no dates recorded</text>')

    # sons
    sy0 = sons_top
    out.append(f'<line x1="{cx}" y1="{lineage_bottom}" '
               f'x2="{cx}" y2="{sy0 - 4}" stroke="#5a5a5a" stroke-width="1.6"/>')
    out.append(f'<line x1="{LEFT + 130}" y1="{sy0 - 4}" x2="{SPOUSE_X + 95}" '
               f'y2="{sy0 - 4}" stroke="#5a5a5a" stroke-width="1.6"/>')
    for j, (nm, note) in enumerate(SONS):
        x = LEFT + 130 + j * 300
        y = sy0
        out.append(f'<line x1="{x + 130}" y1="{sy0 - 4}" x2="{x + 130}" '
                   f'y2="{y}" stroke="#5a5a5a" stroke-width="1.6"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{260}" height="{BOX_H}" rx="5" '
                   f'fill="#eaf1f8" stroke="#1f4e79" stroke-width="1.7"/>')
        out.append(f'<text x="{x + 13}" y="{y + 26}" font-size="13.5" '
                   f'font-weight="600" fill="#111">{esc(nm)}</text>')
        out.append(f'<text x="{x + 13}" y="{y + 44}" font-size="10" '
                   f'fill="#555">{esc(note)}</text>')

    fy = sons_bottom + 30
    out.append(f'<text x="{LEFT}" y="{fy}" font-size="10.5" fill="#8a3a3a" '
               f'font-weight="600">NO ancestor birth date or time is known — '
               f'no ancestor chart was calculated.</text>')
    out.append(f'<text x="{LEFT}" y="{fy + 16}" font-size="10.5" fill="#8a3a3a">'
               f'Kusankur DOB = UNRESOLVED. 03-Jul-1951 is a documentary candidate only.</text>')
    out.append(f'<text x="{LEFT}" y="{fy + 32}" font-size="9.5" fill="#777">'
               f'The Ancestry screenshot does not contain Kusankur or Swarna Sekhar, '
               f'and places Sisir Kumar in the youngest row — recorded as a conflict, not merged.</text>')

    out.append('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" '
               'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
               '<path d="M 0 0 L 10 5 L 0 10 z" fill="#5a5a5a"/>'
               '</marker></defs>')
    out.append('</svg>')

    p = os.path.join(OUT, "paternal_lineage.svg")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print(f"Wrote {p}  ({os.path.getsize(p)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())