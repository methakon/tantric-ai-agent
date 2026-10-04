#!/usr/bin/env python3
"""
build_report.py — one entry point for the HTML → PDF build.

    python3 build_report.py                # design preview (representative years)
    python3 build_report.py --full         # the complete 1981-2053 edition
    python3 build_report.py --qa           # preview + the automated QA gate

The full edition is NOT produced unless --full is given explicitly.
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from kundali_report import render                     # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Kundali HTML->PDF build")
    ap.add_argument("--full", action="store_true",
                    help="render all years instead of the preview subset")
    ap.add_argument("--qa", action="store_true",
                    help="run the automated render QA after building")
    a = ap.parse_args()

    info = render.build(preview=not a.full)
    print(f"html : {info['html']}")
    print(f"pdf  : {info['pdf']}")
    print(f"pages: {info['pages']}")
    print(f"years: {info['years_rendered']}")
    print(f"TOC  : {info['toc_passes']}  stable={info['toc_stable']}")
    if info["toc_passes"].get("missing"):
        print(f"  UNRESOLVED TOC ENTRIES: {info['toc_passes']['missing']}")

    if a.qa:
        import test_render_report as QA
        return QA.main(info["pdf"])
    return 0


if __name__ == "__main__":
    sys.exit(main())