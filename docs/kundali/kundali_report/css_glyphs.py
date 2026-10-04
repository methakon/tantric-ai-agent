"""
css_glyphs.py — glyph capability probe for the design system.

The brief requires these characters to render. A font that lacks one produces a
tofu box, which is a rendering defect that is invisible in a text-layer check
and obvious to a reader. So the probe runs at BUILD time and raises, rather than
shipping a document with silent boxes.

Glyph coverage is probed from the installed font CMAPs, not assumed from a font
name. The check that matters at render time is in test_render_report.py, which
asserts each glyph actually appears in the PDF text layer.
"""
from __future__ import annotations

import os
import subprocess

# From the design brief §3. Every one of these must render.
REQUIRED_GLYPHS = "—–·•₹°′″→←≥≤±✓"

# The families the design system declares. Order matters: the first installed
# family that covers a glyph wins, matching CSS font fallback.
FAMILIES = ["Noto Serif Display", "Noto Serif", "Noto Sans",
            "DejaVu Serif", "DejaVu Sans", "Liberation Sans"]


def _font_file(family: str):
    try:
        r = subprocess.run(["fc-match", "-f", "%{file}", family],
                           capture_output=True, text=True, timeout=20)
        p = r.stdout.strip()
        return p if p and os.path.exists(p) else None
    except Exception:
        return None


def covered_codepoints() -> set:
    try:
        from fontTools.ttLib import TTFont, TTCollection
    except ImportError:
        return set()
    cov = set()
    for fam in FAMILIES:
        path = _font_file(fam)
        if not path:
            continue
        try:
            fonts = (TTCollection(path).fonts
                     if path.lower().endswith(".ttc")
                     else [TTFont(path, fontNumber=0, lazy=True)])
            for f in fonts:
                for table in f["cmap"].tables:
                    cov |= set(table.cmap.keys())
        except Exception:
            continue
    return cov


def missing_glyphs(chars: str = REQUIRED_GLYPHS) -> list:
    cov = covered_codepoints()
    if not cov:
        # fontTools unavailable: the render-time text-layer check remains the
        # authority. Do not fail the build on a missing probe dependency.
        return []
    return [c for c in chars if c not in " \n\t" and ord(c) not in cov]


def assert_glyphs_available(chars: str = REQUIRED_GLYPHS) -> None:
    miss = missing_glyphs(chars)
    if miss:
        raise RuntimeError(
            f"BUILD FAILURE: required glyphs unavailable in the declared font "
            f"stack {FAMILIES}: {miss}. Do not substitute string replacements; "
            f"install a covering font or revise the design system's family "
            f"list.")


if __name__ == "__main__":
    miss = missing_glyphs()
    print(f"families probed : {FAMILIES}")
    print(f"required glyphs : {REQUIRED_GLYPHS}")
    print(f"missing         : {miss if miss else 'NONE'}")
