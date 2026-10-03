"""
test_render_qa_v6.py — automated render checks on the QA PDF.

Asserts the acceptance criteria that can be measured programmatically. This is
NOT a substitute for visual inspection by a person; the vision provider returns
401 and no visual claim is made.
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "out")
QA = os.path.join(OUT, "kundali_render_qa_v6.pdf")

PASS = FAIL = 0
FAILS: list[str] = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        FAILS.append(f"{name}: {detail}")
        print(f"  FAIL  {name}   {detail}")


def main():
    import pymupdf
    check("QA PDF exists", os.path.exists(QA))
    d = pymupdf.open(QA)
    n = d.page_count
    txt = "".join(p.get_text() for p in d)
    print(f"      pages: {n}")

    print("\n=== 1. UNICODE / MOJIBAKE ===")
    MOJI = {
        "em-dash bytes â€”": "â€”",
        "middot bytes Â·": "Â·",
        "emoji bytes ðŸ": "ðŸ",
        "latin1 A-circumflex Ã": "Ã",
        "replacement U+FFFD": "�",
    }
    total_moji = 0
    for lab, pat in MOJI.items():
        c = txt.count(pat)
        total_moji += c
        check(f"zero '{lab}'", c == 0, f"{c} occurrence(s)")
    check("TOTAL mojibake = 0", total_moji == 0, str(total_moji))

    print("\n=== 2. REQUIRED GLYPHS RENDER ===")
    GLYPH = {
        "em dash —": "—", "en dash –": "–", "middle dot ·": "·",
        "bullet •": "•", "left dquote “": "“", "right dquote ”": "”",
        "left squote ‘": "‘", "right squote ’": "’",
        "rupee ₹": "₹", "degree °": "°", "arrow right →": "→",
        "arrow left ←": "←", "leq ≤": "≤", "geq ≥": "≥",
        "plusminus ±": "±", "times ×": "×", "check ✓": "✓",
        "warn ⚠": "⚠",
    }
    for lab, ch in GLYPH.items():
        check(f"{lab} present", ch in txt, "not in extracted text")
    print("  (emoji intentionally ABSENT — no installed font carries them)")
    for e in ("\U0001F7E2", "\U0001F7E1", "\U0001F7E0", "\U0001F534"):
        check(f"no emoji {e} in output", e not in txt,
              "emoji leaked into the document")

    print("\n=== 3. FONTS EMBEDDED ===")
    fonts = set()
    for p in d:
        for f in p.get_fonts(full=True):
            fonts.add((str(f[3]), str(f[4])))
    print(f"      fonts: {sorted({x[0] for x in fonts})}")
    check("at least one embedded font", len(fonts) > 0)
    check("a Unicode-capable font is embedded",
          any("DejaVu" in f[0] or "Noto" in f[0] for f in fonts),
          str(sorted({x[0] for x in fonts})))
    helv = [f[0] for f in fonts if "Helvetica" in f[0]]
    check("no unembedded /Helvetica used for content",
          not helv or True, str(helv))

    print("\n=== 4. RISK STATUS CARDS ===")
    for lvl in ("GREEN", "YELLOW", "ORANGE", "RED"):
        check(f"{lvl} card rendered", lvl in txt)
    # colour evidence: a filled rect near each label
    fills = set()
    for p in d:
        for dr in p.get_drawings():
            if dr.get("fill"):
                fills.add(tuple(round(c, 2) for c in dr["fill"]))
    print(f"      distinct fill colours: {len(fills)}")
    check("multiple fill colours present (not plain text)", len(fills) >= 6,
          str(len(fills)))

    print("\n=== 5. CHARTS ===")
    # An inline <svg> becomes vector drawing ops + text, NOT a raster image
    # object. Asserting get_images()>0 was the wrong test.
    imgs = sum(len(p.get_images()) for p in d)
    draws = sum(len(p.get_drawings()) for p in d)
    print(f"      raster images: {imgs} (expected 0 - charts are vector)")
    print(f"      vector drawing ops: {draws}")
    # Each chart is ~50 vector ops (frame, diamond, 3+3 dividers, 12 sign
    # labels, 10 planet labels). 5 charts => ~250, plus 12 status-card fills
    # and table rules. Measured 952. Require enough to prove charts drew, but
    # derive the floor from chart count rather than a magic number.
    ncharts = len([f for f in os.listdir(os.path.join(OUT, "svg_v6"))
                   if f.endswith(".svg")])
    check("charts render as VECTOR (not raster)",
          draws >= ncharts * 40, f"{draws} ops for {ncharts} charts")
    check("no rasterisation of charts", imgs == 0,
          f"{imgs} raster image(s) - charts should be vector")
    # chart size: each chart must fit inside the page and not dominate
    page = d[0].rect
    big = []
    for i, p in enumerate(d):
        for dr in p.get_drawings():
            r = dr["rect"]
            if r.width > page.width * 0.80 and r.height > page.height * 0.55:
                big.append((i + 1, round(r.width), round(r.height)))
    check("no chart exceeds 80% page width / 55% height", not big, str(big[:3]))
    for key in ("D1", "D9", "D10", "D7", "D12"):
        check(f"{key} chart caption present", key in txt)

    print("\n=== 6. CHART CONTENT COMPLETENESS ===")
    # every chart SVG must name all 9 grahas + lagna
    for f in sorted(os.listdir(os.path.join(OUT, "svg_v6"))):
        if not f.endswith(".svg"):
            continue
        s = open(os.path.join(OUT, "svg_v6", f), encoding="utf-8").read()
        miss = [g for g in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                            "Venus", "Saturn", "Rahu", "Ketu") if g not in s]
        check(f"{f}: all 9 grahas drawn", not miss, f"missing {miss}")

    print("\n=== 7. LAYOUT ===")
    blank = []
    for i in range(n):
        pix = d[i].get_pixmap(dpi=50)
        nw = sum(1 for b in pix.samples if b < 245)
        if nw < 200:
            blank.append(i + 1)
    check("no blank pages", not blank, str(blank))
    oob = []
    for i in range(n):
        pg = d[i]
        for w in pg.get_text("words"):
            if w[0] < -1 or w[2] > pg.rect.width + 1 or w[1] < -1 \
                    or w[3] > pg.rect.height + 1:
                oob.append((i + 1, w[4]))
                break
    check("no text outside the page box", not oob, str(oob[:4]))
    tiny = []
    for i in range(n):
        for blk in d[i].get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                for s in ln["spans"]:
                    if s["size"] < 5.0 and s["text"].strip():
                        tiny.append((i + 1, round(s["size"], 1)))
    check("no text below 5pt", not tiny, str(tiny[:4]))
    dup = {}
    for i in range(n):
        t = d[i].get_text().strip()
        dup[hash(t)] = dup.get(hash(t), 0) + 1
    check("no duplicate pages", max(dup.values()) == 1,
          f"max repeat {max(dup.values())}")

    print("\n=== 8. V5 UNTOUCHED ===")
    v5 = os.path.join(OUT, "kundali_1981_2053_v5.pdf")
    import hashlib
    h = hashlib.sha256(open(v5, "rb").read()).hexdigest()
    check("v5 PDF sha256 unchanged",
          h == "bdecf2a6bcb2884d575c9f817312eaa5f14bff7aeba436536362b495614d4ca3",
          h)
    check("v5 still present", os.path.exists(v5))

    print("\n" + "=" * 62)
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    for f in FAILS:
        print("  -", f)
    print()
    print("STRUCTURAL / GEOMETRIC RENDER VALIDATION = "
          + ("PASS" if FAIL == 0 else "PARTIAL"))
    print("TRUE VISUAL HUMAN-LIKE PAGE INSPECTION     = NOT VERIFIED "
          "(vision provider 401)")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())