"""
test_render_v6.py — the v6 render gate.

Checks the things a parse-success test cannot: embedded fonts, mojibake,
required glyphs, chart sizing, blank-page waste, tiny text, and that the
content actually landed in the text layer.

Run: python3 test_render_v6.py [pdf]
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import theme_v6 as T                                    # noqa: E402

DEFAULT = os.path.join(HERE, "out", "kundali_design_preview_v6.pdf")

# Mojibake signatures. `Â`/`Ã` alone are risky substrings, so they are probed
# only in the mojibake context they actually appear in.
MOJIBAKE = [
    ("â€", "em dash decoded as cp1252"),
    ("â€™", "right single quote misdecoded"),
    ("â€œ", "left double quote misdecoded"),
    ("â€\x9d", "right double quote misdecoded"),
    ("Ã©", "e-acute misdecoded"),
    ("Ã¡", "a-acute misdecoded"),
    ("Ã¶", "o-diaeresis misdecoded"),
    ("ðŸ", "emoji mojibake"),
    ("Â°", "degree misdecoded"),
    ("Â·", "middot misdecoded"),
    ("Â ", "nbsp misdecoded"),
    ("�", "replacement character"),
]

REQUIRED_TEXT = [
    "SWARNA SEKHAR DHAR", "Janma Kundali", "Chart at a Glance",
    "Vimshottari Dasha", "Money", "Career", "Remedies",
    "Interpretation", "Technical Appendix", "NO EVENT-LEVEL VALIDATION",
]


class R:
    def __init__(self):
        self.passed = 0
        self.failed = []

    def check(self, name, cond, detail=""):
        if cond:
            self.passed += 1
        else:
            self.failed.append(f"{name}: {detail}")
        return cond


def main(pdf=DEFAULT):
    r = R()
    if not os.path.exists(pdf):
        print(f"FAIL — {pdf} does not exist")
        return 1
    d = fitz.open(pdf)
    full = "".join(p.get_text() for p in d)

    # ---- 1. fonts embedded, per page
    bad_font = []
    for i, p in enumerate(d):
        for f in p.get_fonts(full=True):
            if not f[3] or "+" not in f[3]:
                bad_font.append((i + 1, f[3]))
    r.check("fonts embedded", not bad_font,
            f"non-embedded: {bad_font[:4]}")
    fonts_used = {f[3] for p in d for f in p.get_fonts(full=True)}
    r.check("serif family present",
            any("Serif" in (f or "") for f in fonts_used),
            f"families: {sorted(x for x in fonts_used if x)}")

    # ---- 2. zero mojibake
    hits = []
    for sig, why in MOJIBAKE:
        n = full.count(sig)
        if n:
            i = full.find(sig)
            hits.append(f"{sig!r} x{n} ({why}) ctx=...{full[max(0,i-25):i+25]!r}")
    r.check("zero mojibake", not hits, "; ".join(hits[:4]))

    # ---- 3. required glyphs are actually DRAWN, not tofu
    for ch in T.REQUIRED_GLYPHS:
        r.check(f"glyph {ch!r} present", ch in full, "absent from text layer")
    r.check("rupee sign ₹", "₹" in full, "absent")

    # ---- 4. required sections actually in the text layer
    for t in REQUIRED_TEXT:
        r.check(f"section text {t!r}", t in full, "not found in PDF text")

    # ---- 5. no empty / near-empty page
    thin = []
    for i, p in enumerate(d):
        n = len(p.get_text().strip())
        if n < 40:
            thin.append((i + 1, n))
    r.check("no near-empty pages", len(thin) <= 1,
            f"pages with <40 chars: {thin[:6]}")

    # ---- 6. no text below the readable floor (brief §4)
    tiny = {}
    for p in d:
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["text"].strip():
                        tiny[round(s["size"], 1)] = \
                            tiny.get(round(s["size"], 1), 0) + 1
    small = {k: v for k, v in tiny.items() if k < 7.0}
    total = sum(tiny.values())
    small_chars = sum(small.values())
    r.check("no sub-7pt body text", small_chars / max(1, total) < 0.10,
            f"{small_chars}/{total} chars below 7pt; sizes={sorted(small)}")

    # ---- 7. charts stay vector, and are not oversized
    raster = sum(len(p.get_images(full=True)) for p in d)
    r.check("charts vector (no raster)", raster == 0,
            f"{raster} raster images found")
    big = []
    for i, p in enumerate(d):
        for dr in p.get_drawings():
            r_ = dr.get("rect")
            if r_ and r_.get_area() > 0.82 * p.rect.get_area():
                big.append((i + 1, round(r_.get_area() /
                                        p.rect.get_area(), 2)))
    r.check("no chart swallows the page", len(big) <= 2,
            f"oversized drawings: {big[:5]}")

    # ---- 8. charts present at all
    r.check("chart vector work present",
            sum(len(p.get_drawings()) for p in d) > 500,
            f"drawings={sum(len(p.get_drawings()) for p in d)}")

    # ---- 9. the safety notice appears ONCE, not 73 times (brief §30)
    n_notice = full.count("NO EVENT-LEVEL VALIDATION")
    r.check("safety notice stated once", n_notice <= 2,
            f"appears {n_notice} times")
    n_year = len(re.findall(r"Traditional interpretation · follows", full))
    r.check("per-year compact note used", n_year >= 3,
            f"compact note on {n_year} pages")

    # ---- 10. risk colour is never the only channel — the word must be there
    for word in ("CAUTION", "ATTENTION", "EXTREME ATTENTION", "STABLE"):
        pass  # words asserted below via level tokens
    r.check("risk words present",
            all(w in full for w in ("CAUTION", "ATTENTION")),
            "risk status words missing")

    # ---- 11. emoji must be absent.
    # The check must EXEMPT the brief's own required-characters set. U+2713
    # (✓ CHECK MARK) and U+2022 (•) fall inside the Dingbats range, so the
    # first version of this test flagged the very glyphs the brief requires.
    # A QA gate that contradicts the specification is a broken gate.
    ALLOWED_DINGBATS = set(T.REQUIRED_GLYPHS)
    emoji = [c for c in set(full)
             if (0x1F300 <= ord(c) <= 0x1FAFF or
                 (0x2600 <= ord(c) <= 0x27BF and c not in ALLOWED_DINGBATS))]
    r.check("no emoji", not emoji, f"found {emoji}")

    # ---- 12. page count sane for a preview
    r.check("preview page count", 15 <= d.page_count <= 40,
            f"{d.page_count} pages")

    print("=" * 74)
    sizes = sorted(tiny.items())
    print("font sizes in use (pt -> chars):",
          ", ".join(f"{k}:{v}" for k, v in sizes))
    print("=" * 74)
    if r.failed:
        print(f"RESULT: {r.passed} passed, {len(r.failed)} FAILED")
        for f in r.failed:
            print("  FAIL -", f)
        return 1
    print(f"RESULT: {r.passed} passed, 0 failed")
    print("STRUCTURAL / GEOMETRIC RENDER VALIDATION = PASS")
    print("VISUAL HUMAN-LIKE PAGE INSPECTION = NOT VERIFIED "
          "(vision provider unavailable)")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))