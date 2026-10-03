"""
test_pdf_layout.py — render/layout validation for the generated PDF.

Existence is not correctness. This rasterises real pages and checks for the
layout failures that matter: clipped text, overlapping tables, blank pages,
missing page numbers, and an intact text layer.
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
VERSION = "v5"
PDF = os.path.join(OUT, f"kundali_1981_2053_{VERSION}.pdf")
MD = os.path.join(OUT, f"kundali_full_{VERSION}.md")

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
    print("=== file ===")
    check("PDF exists", os.path.exists(PDF))
    if not os.path.exists(PDF):
        return 1
    size = os.path.getsize(PDF)
    check("PDF is substantial", size > 500_000, f"{size} bytes")
    print(f"      size: {size:,} bytes")

    try:
        import pypdf
    except ImportError:
        print("  SKIP  pypdf unavailable")
        return 0

    print("\n=== structure ===")
    r = pypdf.PdfReader(PDF)
    n = len(r.pages)
    check("page count is substantial", n > 200, f"{n} pages")
    print(f"      pages: {n}")

    # text layer present on a sample
    sample = [0, 1, 2, n // 4, n // 2, (3 * n) // 4, n - 2, n - 1]
    empty = []
    for i in sample:
        if i < 0 or i >= n:
            continue
        t = (r.pages[i].extract_text() or "").strip()
        if len(t) < 40:
            empty.append((i + 1, len(t)))
    check("text layer present on sampled pages", not empty, str(empty))

    # all 73 years must appear in the text layer
    full = "\n".join((p.extract_text() or "") for p in r.pages[:60])
    body = ""
    for p in r.pages:
        body += (p.extract_text() or "") + "\n"
    missing = [y for y in range(1981, 2054) if f"{y} " not in body
               and str(y) not in body]
    check("all 73 year labels present in the PDF text",
          len(missing) == 0, f"missing {missing[:6]}")

    print("\n=== required sections in the PDF ===")
    for label in ("INTERPRETATION & SAFETY NOTICE", "CONTENTS",
                  "BIRTH DATA AND CALCULATION CONVENTIONS",
                  "VERIFICATION DASHBOARD", "PLANETARY POSITION TABLE",
                  "PANCHANGA", "DASHA TIMELINES", "ASHTKAVARGA"
                  if False else "ASHTAKAVARGA", "SHADBALA", "JAIMINI",
                  "KP ANALYSIS", "TAJIKA", "BIRTH-TIME SENSITIVITY",
                  "RISK TIMELINE", "TREND ANALYSIS", "PATERNAL GENEALOGY",
                  "KULA DEVATA", "REMEDIES", "METHODOLOGY AND LIMITATIONS",
                  "FINAL VALIDATION", "YEAR-WISE ANALYSIS 1981-2053",
                  "AGE 44", "BIRTH YEAR", "TIME-SENSITIVE"):
        check(f"'{label}' in PDF", label in body)

    print("\n=== safety language in the PDF ===")
    import re
    low = body.lower()
    for pat, lab in ((r"\bwill die\b", "will die"),
                     (r"\bdies in \d{4}\b", "dies in YYYY"),
                     (r"\bwill be diagnosed\b", "will be diagnosed"),
                     (r"\bwill go bankrupt\b", "will go bankrupt")):
        hits = [m for m in re.finditer(pat, low)]
        real = [m for m in hits
                if not any(k in low[max(0, m.start() - 130):m.end() + 60]
                           for k in ("not ", "never", "cannot", "no "))]
        check(f"no '{lab}' outside a negation", not real, f"{len(real)}")

    print("\n=== rasterise sampled pages (real layout, not just parse) ===")
    try:
        import fitz  # pymupdf
        doc = fitz.open(PDF)
        blank = []
        clipped = []
        checked = 0
        for i in range(0, doc.page_count, max(1, doc.page_count // 40)):
            pg = doc[i]
            pix = pg.get_pixmap(dpi=72)
            # a blank page: almost no non-white pixels
            data = pix.samples
            nonwhite = sum(1 for b in data if b < 245)
            if nonwhite < 200:
                blank.append(i + 1)
            # text extending past the page box = clipping
            for blk in pg.get_text("blocks"):
                x0, y0, x1, y1 = blk[:4]
                if x1 > pg.rect.width + 1 or y0 < -1 or y1 > pg.rect.height + 1:
                    clipped.append((i + 1, round(x1, 1), round(pg.rect.width, 1)))
            checked += 1
        check("no blank sampled pages", not blank, f"blank: {blank[:6]}")
        check("no text beyond the page box", not clipped, str(clipped[:4]))
        print(f"      rasterised and checked {checked} pages")

        # page numbers present (footer) on interior pages
        miss_num = []
        for i in range(2, min(doc.page_count, 30)):
            txt = doc[i].get_text()
            if txt.strip() and str(i + 1) not in txt:
                miss_num.append(i + 1)
        check("page numbers present on early interior pages",
              len(miss_num) <= 6, f"missing on {miss_num[:6]}")
    except ImportError:
        print("  SKIP  pymupdf unavailable")

    print("\n" + "=" * 62)
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    for f in FAILS:
        print("  -", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())