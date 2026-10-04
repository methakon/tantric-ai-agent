"""
test_render_report.py — the automated render QA gate for the HTML -> PDF build.

Checks the things a successful parse cannot tell you. Every check states what
it measures and why it matters; a check that cannot fail is not a check.

    python3 test_render_report.py [pdf]

Exit 0 = pass. Exit 1 = at least one failure.
"""
from __future__ import annotations

import os
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from kundali_report import structure                       # noqa: E402
from kundali_report.data import loader                    # noqa: E402
from kundali_report.css_glyphs import REQUIRED_GLYPHS, missing_glyphs  # noqa: E402

DEFAULT = os.path.join(HERE, "output", "preview.pdf")

# Mojibake signatures. `Â`/`Ã` alone are risky substrings, so each is probed
# only in the context it actually occurs in.
MOJIBAKE = [
    ("â€", "em/en dash misdecoded"), ("â€™", "right quote misdecoded"),
    ("â€œ", "left quote misdecoded"), ("Ã©", "e-acute misdecoded"),
    ("Ã¡", "a-acute misdecoded"), ("Ã¶", "o-diaeresis misdecoded"),
    ("ðŸ", "emoji misdecoded"), ("Â°", "degree misdecoded"),
    ("Â·", "middot misdecoded"), ("�", "replacement char"),
]

REQUIRED_SECTIONS = [
    "Executive Summary", "Methodology", "Birth Data", "Chart at a Glance",
    "Planetary Positions", "Panchanga", "House Analysis", "Yogas",
    "Ashtakavarga", "Vimshottari Dasha", "Life Themes",
    "Historical Life-Event Validation", "Education Validation",
    "Career Validation", "Marriage", "Family", "Children", "Ancestry",
    "Money", "Property", "Timeline", "Year-by-Year", "Remedies",
    "Technical Appendix", "Validation & Limitations", "Data Sources",
    "Audit Trail",
]

# The NO-GO must survive into the rendered document. If a template ever drops
# the verdict panel, this fails rather than silently shipping a report that
# reads as though the model validated.
VERDICT_MARKERS = [
    "NO-GO",
    "Event-level predictive validity: NOT ESTABLISHED",
    "not be treated as empirically validated predictions",
]


class R:
    def __init__(self):
        self.passed = 0
        self.failed = []

    def check(self, name, ok, detail=""):
        if ok:
            self.passed += 1
            print(f"[PASS] {name}")
        else:
            self.failed.append((name, detail))
            print(f"[FAIL] {name} — {detail}")
        return ok


def main(pdf: str = DEFAULT) -> int:
    r = R()
    if not os.path.exists(pdf):
        print(f"FAIL — {pdf} does not exist. Build it first.")
        return 1
    d = fitz.open(pdf)
    pages = [p.get_text() for p in d]
    full = "".join(pages)

    # ---- 1. fonts embedded on every page
    bad = [(i + 1, f[3]) for i, p in enumerate(d) for f in p.get_fonts(full=True)
           if not f[3] or "+" not in f[3]]
    r.check("fonts embedded", not bad, f"non-embedded: {bad[:5]}")
    fams = {f[3] for p in d for f in p.get_fonts(full=True)}
    r.check("serif family present",
            any("Serif" in (f or "") for f in fams),
            f"families: {sorted(x for x in fams if x)}")

    # ---- 2. zero mojibake
    hits = []
    for sig, why in MOJIBAKE:
        n = full.count(sig)
        if n:
            i = full.find(sig)
            hits.append(f"{sig!r} x{n} ({why}) …{full[max(0,i-30):i+30]!r}")
    r.check("zero mojibake", not hits, "; ".join(hits[:3]))

    # ---- 3. required glyphs present in the TEXT layer
    absent = [g for g in REQUIRED_GLYPHS if g not in full]
    r.check("required glyphs drawn", not absent,
            f"absent from text layer: {absent}")

    # ---- 4. every section present
    missing = [s for s in REQUIRED_SECTIONS if s not in full]
    r.check("all sections rendered", not missing, f"missing: {missing}")

    # ---- 5. NO-GO verdict survived rendering
    vmiss = [m for m in VERDICT_MARKERS if m not in full]
    r.check("NO-GO verdict present", not vmiss, f"missing: {vmiss}")

    # ---- 6. TOC resolved — no placeholder em dashes left
    toc_unresolved = full.count("—\n")
    toc_pages = [p for p in pages if "Contents" in p[:200]]
    r.check("TOC rendered", bool(toc_pages), "no contents page found")
    if toc_pages:
        t = toc_pages[0]
        r.check("TOC page numbers resolved", "—" not in t,
                "an em dash remains where a page number belongs")

    # ---- 7. no blank / near-empty page
    thin = [(i + 1, len(p.strip())) for i, p in enumerate(pages)
            if len(p.strip()) < 40]
    r.check("no near-empty pages", len(thin) <= 1,
            f"pages with <40 chars: {thin[:6]}")

    # ---- 8. text size floor
    sizes = {}
    for p in d:
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["text"].strip():
                        k = round(s["size"], 1)
                        sizes[k] = sizes.get(k, 0) + len(s["text"])
    total = sum(sizes.values())
    small = {k: v for k, v in sizes.items() if k < 7.0}
    r.check("no sub-7pt body text", sum(small.values()) / max(1, total) < 0.10,
            f"{sum(small.values())}/{total} chars below 7pt; {sorted(small)}")

    # ---- 9. charts stay vector
    raster = sum(len(p.get_images(full=True)) for p in d)
    r.check("charts vector", raster == 0, f"{raster} raster images")

    # ---- 10. no chart swallows the page
    big = []
    for i, p in enumerate(d):
        area = p.rect.get_area()
        for dr in p.get_drawings():
            rr = dr.get("rect")
            if rr and rr.get_area() > 0.82 * area:
                big.append((i + 1, round(rr.get_area() / area, 2)))
    r.check("no page-swallowing graphic", len(big) <= 3, f"{big[:5]}")

    # ---- 11. page-break discipline: no orphaned heading
    orphan = []
    for i, p in enumerate(d[:-1]):
        blocks = sorted(p.get_text("dict")["blocks"],
                        key=lambda b: b["bbox"][3])
        if not blocks:
            continue
        last = blocks[-1]
        txt = " ".join(s["text"] for l in last.get("lines", [])
                       for s in l["spans"]).strip()
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if abs(round(s["size"], 1) - 21.0) < 0.4 and \
                            b["bbox"][3] > p.rect.height * 0.75:
                        orphan.append((i + 1, txt[:40]))
    r.check("no orphaned h1 at page foot", not orphan, f"{orphan[:4]}")

    # ---- 12. whitespace: no page mostly empty
    waste = []
    for i, p in enumerate(d):
        blocks = p.get_text("dict")["blocks"]
        if not blocks:
            waste.append((i + 1, 100.0))
            continue
        low = max(b["bbox"][3] for b in blocks)
        blank = 100.0 * (1 - low / p.rect.height)
        if blank > 35:
            waste.append((i + 1, round(blank)))
    r.check("no excessive whitespace", len(waste) <= 3,
            f"{len(waste)} pages over 35% blank: {waste[:6]}")

    # ---- 13. risk colour never the only channel
    r.check("risk words present",
            all(w in full for w in ("CAUTION", "ATTENTION")),
            "risk status words missing from the text layer")

    # ---- 14. no emoji (exempting the brief's required set)
    allowed = set(REQUIRED_GLYPHS)
    emoji = [c for c in set(full)
             if (0x1F300 <= ord(c) <= 0x1FAFF or
                 (0x2600 <= ord(c) <= 0x27BF and c not in allowed))]
    r.check("no emoji", not emoji, f"found {emoji}")

    # ---- 15. birth-time-sensitive years still labelled
    missing_ts = [y for y in sorted(loader.TIME_SENSITIVE)
                  if str(y) not in full]
    r.check("time-sensitive years present", not missing_ts,
            f"absent: {missing_ts}")

    # ---- 16. death-record conflict NOT resolved
    r.check("2018/2019 conflict still open",
            ("UNRESOLVED" in full and "2018" in full and "2019" in full),
            "the documentary conflict appears to have been settled somewhere")

    print()
    print("=" * 74)
    print("font sizes (pt -> chars):",
          ", ".join(f"{k}:{v}" for k, v in sorted(sizes.items())))
    print(f"pages: {d.page_count}   chars: {len(full):,}")
    print("=" * 74)
    if r.failed:
        print(f"RESULT: {r.passed} passed, {len(r.failed)} FAILED")
        for n, det in r.failed:
            print(f"  - {n}: {det}")
        print("\nSTRUCTURAL / GEOMETRIC RENDER VALIDATION = FAIL")
        print("VISUAL HUMAN-LIKE PAGE INSPECTION = NOT VERIFIED "
              "(vision provider unavailable)")
        d.close()
        return 1
    print(f"RESULT: {r.passed} passed, 0 failed")
    print("STRUCTURAL / GEOMETRIC RENDER VALIDATION = PASS")
    print("VISUAL HUMAN-LIKE PAGE INSPECTION = NOT VERIFIED "
          "(vision provider unavailable)")
    d.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))